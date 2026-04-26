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


def _coords_latlng_from_geojson_line(coords: Any) -> list[tuple[float, float]]:
    if not isinstance(coords, list) or len(coords) < 2:
        return []
    out: list[tuple[float, float]] = []
    for c in coords:
        if not isinstance(c, list) or len(c) < 2:
            continue
        lng = float(c[0])
        lat = float(c[1])
        out.append((lat, lng))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="web/public/maps/bangalore_roads_full.geojson")
    ap.add_argument("--out", dest="out", default="web/public/maps/bangalore_roads_graph.json")
    ap.add_argument("--meta-out", dest="meta_out", default="web/public/maps/bangalore_roads_build_meta.json")
    ap.add_argument("--snap-decimals", type=int, default=5, help="Coordinate snapping for intersection merging")
    ap.add_argument("--geom-every", type=int, default=3, help="keep every Nth point in edge geometry (>=1)")
    ap.add_argument("--keep-only-largest-component", action="store_true", default=True)
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

    snap_decimals = int(args.snap_decimals)
    geom_every = max(1, int(args.geom_every))

    # Pass 1: build point adjacency over snapped coordinates.
    adj: dict[tuple[float, float], set[tuple[float, float]]] = {}

    def add_neighbor(a: tuple[float, float], b: tuple[float, float]):
        if a == b:
            return
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    for f in feats:
        if not isinstance(f, dict):
            continue
        geom = f.get("geometry") or {}
        if not isinstance(geom, dict) or geom.get("type") != "LineString":
            continue
        pts = _coords_latlng_from_geojson_line(geom.get("coordinates"))
        if len(pts) < 2:
            continue
        snapped = [snap(lat, lng, decimals=snap_decimals) for (lat, lng) in pts]
        for a, b in zip(snapped, snapped[1:]):
            add_neighbor(a, b)

    # Intersections/endpoints are nodes where degree != 2.
    is_node: dict[tuple[float, float], bool] = {k: (len(v) != 2) for k, v in adj.items()}

    node_id: dict[tuple[float, float], int] = {}
    nodes: list[Node] = []

    def get_node(k: tuple[float, float]) -> int:
        if k in node_id:
            return node_id[k]
        nid = len(nodes)
        node_id[k] = nid
        nodes.append(Node(lat=float(k[0]), lng=float(k[1])))
        return nid

    edges: list[dict[str, Any]] = []

    # Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges
    for f in feats:
        if not isinstance(f, dict):
            continue
        geom = f.get("geometry") or {}
        if not isinstance(geom, dict) or geom.get("type") != "LineString":
            continue
        coords = geom.get("coordinates")
        pts = _coords_latlng_from_geojson_line(coords)
        if len(pts) < 2:
            continue
        props = f.get("properties") or {}
        highway = str((props.get("highway") if isinstance(props, dict) else "") or "")
        name = str((props.get("name") if isinstance(props, dict) else "") or "")

        snapped = [snap(lat, lng, decimals=snap_decimals) for (lat, lng) in pts]
        # Ensure endpoints are treated as nodes.
        if snapped:
            is_node[snapped[0]] = True
            is_node[snapped[-1]] = True

        last_node_k: tuple[float, float] | None = None
        seg_geom: list[list[float]] = []  # [[lat,lng],...]

        def flush(to_k: tuple[float, float]):
            nonlocal last_node_k, seg_geom
            if last_node_k is None:
                last_node_k = to_k
                seg_geom = [[float(to_k[0]), float(to_k[1])]]
                return
            if to_k == last_node_k:
                return
            if len(seg_geom) < 2:
                seg_geom.append([float(to_k[0]), float(to_k[1])])
            else:
                seg_geom[-1] = [float(to_k[0]), float(to_k[1])]

            a_id = get_node(last_node_k)
            b_id = get_node(to_k)

            # Distance along the segment geometry
            dist_m = 0.0
            for (la1, lo1), (la2, lo2) in zip(seg_geom, seg_geom[1:]):
                dist_m += haversine_m(float(la1), float(lo1), float(la2), float(lo2))
            v_kmh = speed_kmh(highway)
            travel_s = dist_m / max(1e-3, (v_kmh * 1000.0 / 3600.0))

            edges.append(
                {
                    "a": int(a_id),
                    "b": int(b_id),
                    "highway": highway,
                    "name": name,
                    "dist_m": round(dist_m, 3),
                    "travel_s": round(travel_s, 4),
                    "geom": [
                        [round(float(p[0]), snap_decimals), round(float(p[1]), snap_decimals)]
                        for idx, p in enumerate(seg_geom)
                        if geom_every <= 1 or idx in (0, len(seg_geom) - 1) or (idx % geom_every) == 0
                    ],
                }
            )

            last_node_k = to_k
            seg_geom = [[float(to_k[0]), float(to_k[1])]]

        # Build contracted segments
        if not snapped:
            continue
        # Start at first point
        last_node_k = snapped[0]
        seg_geom = [[float(snapped[0][0]), float(snapped[0][1])]]
        for k in snapped[1:]:
            seg_geom.append([float(k[0]), float(k[1])])
            if is_node.get(k, False):
                flush(k)

    payload = {
        "meta": {
            "source": str(inp.relative_to(ROOT)).replace("\\", "/"),
            "snap_decimals": snap_decimals,
            "geom_every": geom_every,
            "speed_kmh": SPEED_KMH,
            "keep_only_largest_component": True,
        },
        "nodes": [{"lat": round(n.lat, snap_decimals), "lng": round(n.lng, snap_decimals)} for n in nodes],
        "edges": edges,
    }

    # Keep only the largest connected component (by node count) to satisfy routing coverage.
    g3 = nx.Graph()
    g3.add_nodes_from(range(len(nodes)))
    for e in edges:
        g3.add_edge(int(e["a"]), int(e["b"]))
    comps3 = list(nx.connected_components(g3))
    keep_nodes = max(comps3, key=lambda c: len(c)) if comps3 else set()
    keep_nodes_set = set(int(x) for x in keep_nodes)

    # Remap nodes to a compact id space.
    id_map: dict[int, int] = {}
    new_nodes: list[dict[str, float]] = []
    for old_id in sorted(keep_nodes_set):
        id_map[old_id] = len(new_nodes)
        n = nodes[old_id]
        new_nodes.append({"lat": round(float(n.lat), snap_decimals), "lng": round(float(n.lng), snap_decimals)})

    new_edges: list[dict[str, Any]] = []
    for e in edges:
        a = int(e["a"])
        b = int(e["b"])
        if a not in id_map or b not in id_map:
            continue
        ee = dict(e)
        ee["a"] = id_map[a]
        ee["b"] = id_map[b]
        new_edges.append(ee)

    new_edges.sort(key=lambda e: (int(e["a"]), int(e["b"]), str(e.get("highway") or ""), str(e.get("name") or "")))

    payload["nodes"] = new_nodes
    payload["edges"] = new_edges

    out_text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    out.write_text(out_text, encoding="utf-8")

    sha_in = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    sha_out = hashlib.sha256(out_text.encode("utf-8")).hexdigest()

    # Largest component coverage is 1.0 by construction (remapped), but report ratios vs raw.
    raw_node_count = len(nodes)
    kept_node_count = len(new_nodes)
    coverage = (kept_node_count / max(1, raw_node_count)) if raw_node_count else 0.0

    meta = {
        "input": {"path": str(inp.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_in},
        "output": {"path": str(out.relative_to(ROOT)).replace("\\", "/"), "sha256": sha_out},
        "params": {
            "snap_decimals": snap_decimals,
            "geom_every": geom_every,
            "keep_only_largest_component": True,
            "speed_kmh": SPEED_KMH,
        },
        "counts": {
            "features": len(feats),
            "nodes_raw": raw_node_count,
            "nodes_kept": kept_node_count,
            "edges": len(new_edges),
            "kept_node_ratio": round(float(coverage), 6),
        },
    }
    meta_out.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")

    print(f"Wrote {out} nodes={kept_node_count} edges={len(new_edges)} kept_ratio={coverage:.3f}")
    print(f"Wrote {meta_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

