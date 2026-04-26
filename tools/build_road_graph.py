from __future__ import annotations

import argparse
import json
import hashlib
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any

import networkx as nx


ROOT = Path(__file__).resolve().parents[1]


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


SPEED_KMH = {
    "motorway": 65,
    "trunk": 60,
    "primary": 45,
    "secondary": 35,
    "tertiary": 28,
    "residential": 22,
    "service": 16,
}


def speed_kmh(highway: str) -> float:
    return float(SPEED_KMH.get(highway, 28))


@dataclass(frozen=True)
class Node:
    lat: float
    lng: float


def snap(lat: float, lng: float, *, decimals: int) -> tuple[float, float]:
    return (round(lat, decimals), round(lng, decimals))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="web/public/maps/bangalore_roads_full.geojson")
    ap.add_argument("--out", dest="out", default="web/public/maps/bangalore_roads_graph.json")
    ap.add_argument("--meta-out", dest="meta_out", default="web/public/maps/bangalore_roads_build_meta.json")
    ap.add_argument("--snap-decimals", type=int, default=5, help="Coordinate snapping for intersection merging")
    ap.add_argument("--drop-components-under-edges", type=int, default=200)
    args = ap.parse_args()

    inp = (ROOT / args.inp).resolve()
    out = (ROOT / args.out).resolve()
    meta_out = (ROOT / args.meta_out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    raw_text = inp.read_text(encoding="utf-8")
    gj = json.loads(raw_text)
    feats = gj.get("features", [])
    if not isinstance(feats, list):
        raise SystemExit("invalid geojson: features[] missing")

    node_id: dict[tuple[float, float], int] = {}
    nodes: list[Node] = []
    edges: list[dict[str, Any]] = []

    def get_node(lat: float, lng: float) -> int:
        k = snap(lat, lng, decimals=args.snap_decimals)
        if k in node_id:
            return node_id[k]
        nid = len(nodes)
        node_id[k] = nid
        nodes.append(Node(lat=float(k[0]), lng=float(k[1])))
        return nid

    for f in feats:
        if not isinstance(f, dict):
            continue
        geom = f.get("geometry") or {}
        if not isinstance(geom, dict) or geom.get("type") != "LineString":
            continue
        coords = geom.get("coordinates")
        if not isinstance(coords, list) or len(coords) < 2:
            continue
        props = f.get("properties") or {}
        highway = str((props.get("highway") if isinstance(props, dict) else "") or "")
        name = str((props.get("name") if isinstance(props, dict) else "") or "")

        # Coordinates are [lng,lat] in GeoJSON.
        pts = [(float(c[1]), float(c[0])) for c in coords if isinstance(c, list) and len(c) >= 2]
        if len(pts) < 2:
            continue

        # Build segment edges between consecutive points. This preserves curvature.
        for (lat1, lng1), (lat2, lng2) in zip(pts, pts[1:]):
            a = get_node(lat1, lng1)
            b = get_node(lat2, lng2)
            if a == b:
                continue
            dist_m = haversine_m(lat1, lng1, lat2, lng2)
            v_kmh = speed_kmh(highway)
            travel_s = dist_m / max(1e-3, (v_kmh * 1000.0 / 3600.0))
            edges.append(
                {
                    "a": a,
                    "b": b,
                    "highway": highway,
                    "name": name,
                    "dist_m": round(dist_m, 3),
                    "travel_s": round(travel_s, 4),
                }
            )

    # Prune tiny disconnected components for performance + routing consistency.
    g = nx.Graph()
    g.add_nodes_from(range(len(nodes)))
    for e in edges:
        g.add_edge(int(e["a"]), int(e["b"]))

    keep_edges: set[tuple[int, int]] = set()
    comps = list(nx.connected_components(g))
    # Keep largest component, plus any component with >= threshold edges
    # (edge-count approximated by counting edges internal to component).
    comps_sorted = sorted(comps, key=lambda c: len(c), reverse=True)
    largest = comps_sorted[0] if comps_sorted else set()
    for comp in comps_sorted:
        if comp is largest:
            keep = True
        else:
            # count edges internal to comp
            sub = g.subgraph(comp)
            keep = sub.number_of_edges() >= int(args.drop_components_under_edges)
        if not keep:
            continue
        for (u, v) in g.subgraph(comp).edges():
            a, b = (int(u), int(v))
            keep_edges.add((a, b) if a < b else (b, a))

    pruned_edges: list[dict[str, Any]] = []
    for e in edges:
        a = int(e["a"])
        b = int(e["b"])
        k = (a, b) if a < b else (b, a)
        if k in keep_edges:
            pruned_edges.append(e)

    # Deterministic ordering.
    pruned_edges.sort(key=lambda e: (int(e["a"]), int(e["b"]), str(e.get("highway") or ""), str(e.get("name") or "")))

    nodes_json = [{"lat": round(n.lat, args.snap_decimals), "lng": round(n.lng, args.snap_decimals)} for n in nodes]

    payload = {
        "meta": {
            "source": str(inp.relative_to(ROOT)).replace("\\", "/"),
            "snap_decimals": args.snap_decimals,
            "speed_kmh": SPEED_KMH,
            "drop_components_under_edges": int(args.drop_components_under_edges),
        },
        "nodes": nodes_json,
        "edges": pruned_edges,
    }

    out_text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    out.write_text(out_text, encoding="utf-8")

    sha_in = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    sha_out = hashlib.sha256(out_text.encode("utf-8")).hexdigest()

    # Largest component coverage
    g2 = nx.Graph()
    g2.add_nodes_from(range(len(nodes)))
    for e in pruned_edges:
        g2.add_edge(int(e["a"]), int(e["b"]))
    comps2 = list(nx.connected_components(g2))
    largest2 = max((len(c) for c in comps2), default=0)
    coverage = (largest2 / max(1, len(nodes))) if nodes else 0.0

    meta = {
        "input": {"path": str(inp.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_in},
        "output": {"path": str(out.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_out},
        "params": {
            "snap_decimals": int(args.snap_decimals),
            "drop_components_under_edges": int(args.drop_components_under_edges),
            "speed_kmh": SPEED_KMH,
        },
        "counts": {
            "features": len(feats),
            "nodes": len(nodes),
            "edges_raw": len(edges),
            "edges_pruned": len(pruned_edges),
            "largest_component_node_coverage": round(float(coverage), 6),
        },
    }
    meta_out.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote {out} nodes={len(nodes)} edges={len(pruned_edges)} coverage={coverage:.3f}")
    print(f"Wrote {meta_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

