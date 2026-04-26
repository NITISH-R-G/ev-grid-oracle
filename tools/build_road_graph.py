from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from pathlib import Path


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
    ap.add_argument("--in", dest="inp", default="web/public/maps/bangalore_roads_demo.geojson")
    ap.add_argument("--out", dest="out", default="web/public/maps/bangalore_roads_graph.json")
    ap.add_argument("--snap-decimals", type=int, default=5, help="Coordinate snapping for intersection merging")
    args = ap.parse_args()

    inp = (ROOT / args.inp).resolve()
    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    gj = json.loads(inp.read_text(encoding="utf-8"))
    feats = gj.get("features", [])
    if not isinstance(feats, list):
        raise SystemExit("invalid geojson: features[] missing")

    node_id: dict[tuple[float, float], int] = {}
    nodes: list[Node] = []
    edges: list[dict] = []

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
                    "dist_m": dist_m,
                    "travel_s": travel_s,
                }
            )

    payload = {
        "meta": {
            "source": str(inp.relative_to(ROOT)).replace("\\", "/"),
            "snap_decimals": args.snap_decimals,
            "speed_kmh": SPEED_KMH,
        },
        "nodes": [{"lat": n.lat, "lng": n.lng} for n in nodes],
        "edges": edges,
    }
    out.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Wrote {out} nodes={len(nodes)} edges={len(edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

