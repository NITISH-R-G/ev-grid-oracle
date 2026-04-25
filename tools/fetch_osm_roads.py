from __future__ import annotations

import argparse
import json
import math
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@dataclass(frozen=True)
class BBox:
    lat_s: float
    lng_w: float
    lat_n: float
    lng_e: float


def _fetch_overpass(query: str, *, timeout_s: int = 120) -> dict:
    data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        OVERPASS_URL,
        data=data,
        method="POST",
        headers={
            # Overpass will sometimes reject requests without explicit headers.
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": "EVGridOracle/0.1 (hackathon demo; contact: local)",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def _simplify_line(coords: list[list[float]], *, max_points: int) -> list[list[float]]:
    # Very cheap simplification: uniform sampling.
    if len(coords) <= max_points:
        return coords
    step = max(1, len(coords) // max_points)
    out = coords[::step]
    if out[-1] != coords[-1]:
        out.append(coords[-1])
    return out


def _to_feature_collection(osm: dict, *, max_points_per_way: int) -> dict:
    nodes: dict[int, tuple[float, float]] = {}
    ways: list[dict] = []
    for el in osm.get("elements", []):
        if el.get("type") == "node":
            nodes[int(el["id"])] = (float(el["lon"]), float(el["lat"]))
        elif el.get("type") == "way":
            ways.append(el)

    feats: list[dict] = []
    for w in ways:
        tags = w.get("tags", {}) or {}
        hw = tags.get("highway")
        if not hw:
            continue
        nds = w.get("nodes", [])
        coords: list[list[float]] = []
        for nid in nds:
            p = nodes.get(int(nid))
            if p is None:
                continue
            lon, lat = p
            coords.append([lon, lat])
        if len(coords) < 2:
            continue
        coords = _simplify_line(coords, max_points=max_points_per_way)
        feats.append(
            {
                "type": "Feature",
                "properties": {
                    "highway": hw,
                    "name": tags.get("name", ""),
                },
                "geometry": {"type": "LineString", "coordinates": coords},
            }
        )

    return {"type": "FeatureCollection", "features": feats}


def build_query(bbox: BBox) -> str:
    # Keep only road-ish ways for performance.
    # bbox order in Overpass: (south,west,north,east)
    bbox_str = f"({bbox.lat_s},{bbox.lng_w},{bbox.lat_n},{bbox.lng_e})"
    return f"""
[out:json][timeout:120];
(
  way["highway"~"motorway|trunk|primary|secondary|tertiary"]{bbox_str};
);
(._;>;);
out body;
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="web/public/maps/bangalore_roads.geojson")
    ap.add_argument("--max-points-per-way", type=int, default=120)
    ap.add_argument("--sleep", type=float, default=0.0, help="sleep seconds before request (rate limiting)")

    # Bangalore-ish bbox (tweakable)
    ap.add_argument("--lat-s", type=float, default=12.83)
    ap.add_argument("--lng-w", type=float, default=77.45)
    ap.add_argument("--lat-n", type=float, default=13.14)
    ap.add_argument("--lng-e", type=float, default=77.78)
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    bbox = BBox(lat_s=args.lat_s, lng_w=args.lng_w, lat_n=args.lat_n, lng_e=args.lng_e)
    q = build_query(bbox)

    if args.sleep > 0:
        time.sleep(args.sleep)

    osm = _fetch_overpass(q)
    fc = _to_feature_collection(osm, max_points_per_way=args.max_points_per_way)

    out.write_text(json.dumps(fc), encoding="utf-8")
    print(f"Wrote {out} with {len(fc['features'])} road features")


if __name__ == "__main__":
    main()

