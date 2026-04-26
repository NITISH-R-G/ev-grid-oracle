# Bangalore OSM Offline Extract (Option B) — Design

## Goal
Ship an **offline, pre-baked Bangalore road extract** that includes **all drivable roads** (not just arterials) while still rendering and routing smoothly on **HF Spaces CPU** with **100–500 vehicles**.

This is the “Option B” choice: **dense realism** for hackathon wow-factor, with **smart pruning** to keep performance predictable.

## Non-goals
- No live Overpass/Mapbox calls at runtime (HF Spaces reliability).
- No full India/KA extract (too large and slow).
- No pedestrian/cycle/footpath routing (keep to drivable network).

## Source of truth (repo files)
Committed assets under `web/public/maps/`:
- `bangalore_roads_full.geojson` — offline OSM extract (drivable ways only)
- `bangalore_roads_graph.json` — compact weighted graph for server routing (nodes/edges)
- (optional) `bangalore_roads_render.json` — simplified path list for deck.gl rendering if GeoJSON is too heavy

Runtime behavior:
- Frontend renders roads + routes from the offline files (no external APIs).
- Server loads `bangalore_roads_graph.json` once and returns road-following polylines.

## Extract specification
### Geographic coverage
- Bounding polygon: Bangalore Urban footprint (preferred) or bounding box around:
  - lat: 12.75–13.18
  - lng: 77.35–77.85

### Road inclusion (drivable only)
Include OSM `highway` types:
- `motorway`, `trunk`, `primary`, `secondary`, `tertiary`, `residential`, `service`

Exclude:
- `footway`, `path`, `cycleway`, `steps`, `pedestrian`, `corridor`, `track` (unless explicitly needed later)

### Pruning rules (performance)
- Drop disconnected components smaller than a threshold (e.g. < 200 edges).
- Optional geometry simplification (Douglas–Peucker) with a small tolerance to reduce vertex count **without straightening key curves**.
- Cap overall vertex count target (guideline): \(\le 1.5–3.0M\) coordinates for GeoJSON; if above, produce a simplified render file.

## Graph build specification
Input: `bangalore_roads_full.geojson`

Outputs:
- Nodes: snapped intersections/endpoints (coordinate snap, e.g. 5 decimals)
- Edges: **segment-to-segment** links that preserve curvature
- Edge weights:
  - `dist_m` via haversine
  - `speed_kmh` by road type (config table)
  - `travel_s = dist_m / speed_mps`

Routing:
- Server shortest path by `travel_s`
- Polyline returned as `[lat, lng]` list with **>2 points** for typical trips

## Training integration
Training environment uses the same prebuilt graph:
- Action schema: `CURRENT_NODE`, `NEXT_NODE` (connected neighbor only)
- Anti-cheat:
  - invalid current node → fail
  - non-neighbor next node → fail
  - episode caps → stop
- Reward:
  - time penalty (travel_s)
  - distance-to-target shaping
  - strong penalties for anti-cheat flags

## Acceptance checks
1. **Visual realism**: dense local streets visible at zoom 12–14 (not only highways).
2. **Routing realism**: server route polyline usually has **> 20 points** and follows curves.
3. **Performance**: 100 vehicles animating, no UI lockups on HF Spaces CPU.
4. **Determinism**: graph build is deterministic given the same input file.
5. **No runtime fetch**: demo works offline (only tile basemap fetches, or none if we later switch to offline tiles).

## Rollout plan
1. Add a one-time **extract tool** that takes a downloaded OSM extract (GeoJSON) and produces the committed outputs.
2. Replace current `bangalore_roads_demo.geojson` with the full extract for rendering.
3. Regenerate `bangalore_roads_graph.json` and ensure server/router loads it.
4. Update training notebook to reflect the final graph size + constraints (already aligned).

