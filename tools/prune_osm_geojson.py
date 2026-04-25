from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ev_grid_oracle.city_graph import STATIONS


def _pad_bbox(lat_lo: float, lat_hi: float, lng_lo: float, lng_hi: float, pad_deg: float) -> tuple[float, float, float, float]:
    return lat_lo - pad_deg, lat_hi + pad_deg, lng_lo - pad_deg, lng_hi + pad_deg


def _line_intersects_bbox(coords: list[list[float]], lat_lo: float, lat_hi: float, lng_lo: float, lng_hi: float) -> bool:
    # Cheap bbox test: any point inside OR segment crosses bbox edges (approx via point-in bbox only).
    for lon, lat in coords:
        if lat_lo <= lat <= lat_hi and lng_lo <= lon <= lng_hi:
            return True
    return False


def _simplify_uniform(coords: list[list[float]], *, max_points: int) -> list[list[float]]:
    if len(coords) <= max_points:
        return coords
    step = max(1, len(coords) // max_points)
    out = coords[::step]
    if out[-1] != coords[-1]:
        out.append(coords[-1])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", type=str, default="web/public/maps/bangalore_roads.geojson")
    ap.add_argument("--out", type=str, default="web/public/maps/bangalore_roads_demo.geojson")
    ap.add_argument("--pad-deg", type=float, default=0.06)
    ap.add_argument("--max-features", type=int, default=1400)
    ap.add_argument("--max-points-per-way", type=int, default=40)
    args = ap.parse_args()

    inp = Path(args.inp)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    lats = [s.lat for s in STATIONS]
    lngs = [s.lng for s in STATIONS]
    lat_lo, lat_hi = min(lats), max(lats)
    lng_lo, lng_hi = min(lngs), max(lngs)
    lat_lo, lat_hi, lng_lo, lng_hi = _pad_bbox(lat_lo, lat_hi, lng_lo, lng_hi, args.pad_deg)

    gj = json.loads(inp.read_text(encoding="utf-8"))
    feats_in = gj.get("features", [])
    if not isinstance(feats_in, list):
        raise SystemExit("Invalid GeoJSON: missing features[]")

    # Keep the demo readable: arterials only (tertiary+ creates “hairball” maps fast).
    allowed_hw = {"motorway", "trunk", "primary", "secondary"}

    out_feats: list[dict] = []
    for f in feats_in:
        if len(out_feats) >= args.max_features:
            break
        if not isinstance(f, dict):
            continue
        geom = f.get("geometry")
        if not isinstance(geom, dict) or geom.get("type") != "LineString":
            continue
        coords = geom.get("coordinates")
        if not isinstance(coords, list) or len(coords) < 2:
            continue

        props = f.get("properties", {}) or {}
        hw = str(props.get("highway", ""))
        if hw not in allowed_hw:
            continue

        if not _line_intersects_bbox(coords, lat_lo, lat_hi, lng_lo, lng_hi):
            continue

        coords2 = _simplify_uniform(coords, max_points=args.max_points_per_way)
        out_feats.append(
            {
                "type": "Feature",
                "properties": {"highway": hw, "name": str(props.get("name", "") or "")},
                "geometry": {"type": "LineString", "coordinates": coords2},
            }
        )

    out.write_text(json.dumps({"type": "FeatureCollection", "features": out_feats}, indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(out_feats)} features (bbox around {len(STATIONS)} stations)")


if __name__ == "__main__":
    main()
