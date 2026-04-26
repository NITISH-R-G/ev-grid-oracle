from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


KEEP_HIGHWAYS_RENDER = {
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "residential",
    # drop "service" by default to reduce clutter/size
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="web/public/maps/bangalore_roads_full.geojson")
    ap.add_argument("--out", dest="out", default="web/public/maps/bangalore_roads_render.json")
    ap.add_argument("--every", type=int, default=4, help="keep every Nth point in each linestring (>=1)")
    ap.add_argument("--max-features", type=int, default=120_000)
    args = ap.parse_args()

    inp = (ROOT / args.inp).resolve()
    out = (ROOT / args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    obj = json.loads(inp.read_text(encoding="utf-8"))
    feats = obj.get("features", [])
    if not isinstance(feats, list):
        raise SystemExit("invalid geojson: missing features")

    every = max(1, int(args.every))
    max_features = int(args.max_features)

    rows: list[dict[str, Any]] = []
    for f in feats:
        if len(rows) >= max_features:
            break
        if not isinstance(f, dict):
            continue
        geom = f.get("geometry") or {}
        if not isinstance(geom, dict) or geom.get("type") != "LineString":
            continue
        props = f.get("properties") or {}
        hw = str((props.get("highway") if isinstance(props, dict) else "") or "")
        if hw and hw not in KEEP_HIGHWAYS_RENDER:
            continue
        coords = geom.get("coordinates")
        if not isinstance(coords, list) or len(coords) < 2:
            continue
        out_coords = []
        for i, c in enumerate(coords):
            if not isinstance(c, list) or len(c) < 2:
                continue
            if every > 1 and (i % every) != 0 and i not in (0, len(coords) - 1):
                continue
            out_coords.append([float(c[0]), float(c[1])])
        if len(out_coords) < 2:
            continue
        rows.append({"highway": hw, "path": out_coords})

    out.write_text(json.dumps(rows, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {out} paths={len(rows)} every={every}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

