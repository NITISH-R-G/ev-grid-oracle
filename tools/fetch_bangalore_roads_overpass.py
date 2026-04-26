from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


DEFAULT_HIGHWAYS = [
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "residential",
    "service",
]


def _chunk(xs: list[str], n: int) -> list[list[str]]:
    out: list[list[str]] = []
    for i in range(0, len(xs), n):
        out.append(xs[i : i + n])
    return out


def _overpass_query(bbox: tuple[float, float, float, float], highways: list[str]) -> str:
    south, west, north, east = bbox
    # Use `out geom` so each way includes geometry points (no extra node fetch).
    # Split the highway filter into OR clauses to avoid huge regexes.
    clauses = "".join([f'way["highway"="{h}"]({south},{west},{north},{east});' for h in highways])
    return f"[out:json][timeout:180];({clauses});out geom;"


def _http_post(url: str, data: dict[str, str], *, retries: int = 3) -> bytes:
    body = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("content-type", "application/x-www-form-urlencoded")
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=240) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt >= retries:
                raise
            time.sleep(1.25 * attempt)
    raise RuntimeError("overpass request failed") from last_err


def _to_geojson(overpass_json: dict[str, Any], *, simplify_every: int) -> dict[str, Any]:
    feats: list[dict[str, Any]] = []
    for el in overpass_json.get("elements", []):
        if not isinstance(el, dict):
            continue
        if el.get("type") != "way":
            continue
        tags = el.get("tags") or {}
        if not isinstance(tags, dict):
            tags = {}
        hw = str(tags.get("highway") or "")
        name = str(tags.get("name") or "")
        geom = el.get("geometry")
        if not isinstance(geom, list) or len(geom) < 2:
            continue

        coords = []
        for i, p in enumerate(geom):
            if simplify_every > 1 and (i % simplify_every) != 0 and i not in (0, len(geom) - 1):
                continue
            if not isinstance(p, dict):
                continue
            lat = p.get("lat")
            lon = p.get("lon")
            if lat is None or lon is None:
                continue
            coords.append([float(lon), float(lat)])  # GeoJSON: [lng,lat]
        if len(coords) < 2:
            continue

        feats.append(
            {
                "type": "Feature",
                "properties": {"highway": hw, "name": name, "osm_id": el.get("id")},
                "geometry": {"type": "LineString", "coordinates": coords},
            }
        )

    return {"type": "FeatureCollection", "features": feats}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="web/public/maps/bangalore_roads_full.geojson")
    ap.add_argument("--bbox", default="12.75,77.35,13.18,77.85", help="south,west,north,east")
    ap.add_argument("--highways", default=",".join(DEFAULT_HIGHWAYS))
    ap.add_argument("--simplify-every", type=int, default=2, help="keep every Nth point per way (>=1)")
    ap.add_argument("--endpoint", default="https://overpass-api.de/api/interpreter")
    args = ap.parse_args()

    south, west, north, east = [float(x.strip()) for x in str(args.bbox).split(",")]
    bbox = (south, west, north, east)
    highways = [h.strip() for h in str(args.highways).split(",") if h.strip()]

    q = _overpass_query(bbox, highways)
    raw = _http_post(args.endpoint, {"data": q})
    obj = json.loads(raw.decode("utf-8"))
    gj = _to_geojson(obj, simplify_every=max(1, int(args.simplify_every)))

    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(gj), encoding="utf-8")
    print(f"Wrote {out} features={len(gj.get('features', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

