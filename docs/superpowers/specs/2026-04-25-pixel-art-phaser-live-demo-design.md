## EV Grid Oracle — Pixel-Art Phaser Live Demo (Design Spec)

### Goal
Deliver a judge-wowing **2D pixel-art animated** web demo where **EV sprites move along Bangalore roads** on a “Google-maps-like” (but legally safe) base map. The demo supports:

- **Baseline vs Oracle** policy toggle (Oracle uses LoRA if available; fallback allowed).
- **Two camera modes**:
  - **City view** (whole city)
  - **Follow EV** (zoom + pan following the active EV) with **minimap**
- **Cinematic cues**: stress pulses on stations, route glow/particles, HUD KPIs.

### Legal / Data Constraints
- Do **not** use Google Maps tiles or copyrighted map art.
- Use **OpenStreetMap** geometry (roads) via Overpass API.
- Cache processed map data in-repo for deterministic demos (no network dependency at runtime).

### Architecture Overview
Two processes (local dev) or one container (Space):

1) **Python API (FastAPI)**
- Lives in the existing `server/app.py` FastAPI app.
- Adds lightweight demo routes under `/demo/*` that wrap `EVGridCore`.
- Maintains per-session environment state in memory keyed by `session_id`.

2) **Web Client (Vite + Phaser)**
- Serves a Phaser scene rendering:
  - Map (roads) in pixel-art style
  - Stations as glowing nodes
  - EV sprite moving along a path
- Calls `/demo/*` endpoints to advance the simulation and fetch events.

### Demo API (v0)
All responses JSON, all requests JSON.

- `POST /demo/new`
  - Creates a new session with seed and returns initial state.
  - Request: `{ "seed": 123 }`
  - Response: `{ "session_id": "...", "obs": { ... }, "station_nodes": [...], "map_bbox": {...} }`

- `POST /demo/step`
  - Advances one tick.
  - Request: `{ "session_id": "...", "mode": "baseline"|"oracle", "oracle_lora_repo": "user/repo"|"", "follow_ev": true|false }`
  - Response: `{ "obs": { ... }, "event": { "type": "route", "from": {...}, "to": {...}, "path": [[x,y]...], "ev_id": "EV-001" } }`

- `GET /demo/state?session_id=...`
  - Returns the latest observation + derived render-friendly values (stations, active EV).

Notes:
- v0 path is allowed to be a polyline from **station-to-station** (graph shortest path), then later upgraded to road-following using OSM polylines.
- v0 should be deterministic for a given seed.

### Map Data Pipeline (v1)
Add an offline caching script:

- `tools/fetch_osm_roads.py`
  - Downloads roads for Bangalore bounding box.
  - Keeps selected highway types (motorway/trunk/primary/secondary/tertiary/residential).
  - Simplifies geometry and exports `assets/maps/bangalore_roads.geojson`.

Client loads this GeoJSON once and renders roads with:
- road hierarchy widths/colors
- render-to-texture then pixelate (downscale + nearest-neighbor)

### Rendering & Pixel-Art Style
Style targets:
- 16-bit vibe (SNES-era), crisp edges, tasteful glow.
- Dark city background, high-contrast road layers, minimal labels.

Effects:
- Station glow intensity ∝ load or queue.
- “Stress pulse” ring when station load > 85%.
- Route glow + particle trail for the selected EV.

### Cameras
- City view: fixed camera framing bbox of map.
- Follow view: camera centers on EV sprite, smooth lerp + zoom-in.
- Minimap: small overlay showing entire city + current camera viewport rect.

### TDD / Validation
Tracer-bullet tests:
- Demo API `POST /demo/new` returns `session_id` and a valid observation shape.
- Demo API `POST /demo/step` returns an `event` with a non-empty polyline path when a route action is taken.
- Route interpolation helper returns deterministic positions at \(t=0, 0.5, 1.0\).

### Non-goals (for hackathon speed)
- Perfect road snapping day-1 (acceptable to start with graph path between station nodes).
- Multiplayer web sockets (polling is fine).

### Rollout Plan
- v0 (today): API + Phaser scene with station graph, EV sprite movement, camera toggle.
- v1: OSM GeoJSON roads and pixelation pipeline.
- v2: split-screen baseline vs oracle with synchronized ticks.

