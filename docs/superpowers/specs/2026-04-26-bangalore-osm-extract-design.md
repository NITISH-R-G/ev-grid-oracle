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
- Hard caps (enforced by tooling):
  - `bangalore_roads_full.geojson` \(\le\) **60 MB**
  - `bangalore_roads_graph.json` \(\le\) **25 MB**
  - If caps are exceeded, generate `bangalore_roads_render.json` (simplified paths) and the frontend must prefer it for rendering.

### Reproducibility (non-negotiable)
- The build must be deterministic given the same input:
  - stable sorting of nodes/edges
  - fixed float rounding for coordinates and weights
  - JSON written with stable key ordering
- Record build metadata alongside outputs:
  - input file SHA256
  - bbox/polygon identifier
  - snap precision, simplify tolerance, prune threshold
  - tool versions
  - output counts (nodes, edges, vertices)
  - saved as `web/public/maps/bangalore_roads_build_meta.json`

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

### Graph invariants (must hold)
- Every edge references existing node ids.
- Every node has finite `lat/lng` within the selected polygon/bbox.
- Graph is explicitly **undirected** (for v1); neighbor relation must be symmetric.
- Largest connected component contains **\(\ge 95\%\)** of nodes after pruning (or fail the build).

## Training integration
Training environment uses the same prebuilt graph:
- Action schema: `CURRENT_NODE`, `NEXT_NODE` (connected neighbor only)
- Anti-cheat:
  - invalid current node → terminate with negative reward
  - non-neighbor next node (“teleportation”) → terminate with negative reward
  - ignore any agent attempts to redefine state; env is source of truth
  - episode caps → stop deterministically
- Reward:
  - time penalty (travel_s)
  - distance-to-target shaping
  - strong penalties for anti-cheat flags
  - log reward breakdown every step (time, shaping, arrive, cheat)

## Acceptance checks
1. **Coverage**: drivable highways included: motorway→service; pedestrian-only ways excluded.
2. **Routing realism**: median polyline length **\(\ge 20\)** points over a fixed OD benchmark set (e.g. 25 random station pairs).
3. **Performance (HF Spaces CPU)**:
   - graph load + router init \(\le\) **2.0s**
   - frontend first interactive render \(\le\) **6.0s**
   - 100 vehicles: no long-frame freezes (no single frame > 250ms during a 30s scripted run)
4. **Determinism**: re-running build on the same input produces identical output SHA256 for `bangalore_roads_graph.json`.
5. **No runtime fetch**: demo uses only committed road files; external calls limited to basemap tiles (or none if we later switch to offline tiles).

## Rollout plan
1. Add a one-time **extract tool** that takes a downloaded OSM extract (GeoJSON) and produces the committed outputs.
2. Replace current `bangalore_roads_demo.geojson` with the full extract for rendering.
3. Regenerate `bangalore_roads_graph.json` and ensure server/router loads it.
4. Update training notebook to reflect the final graph size + constraints (already aligned).

