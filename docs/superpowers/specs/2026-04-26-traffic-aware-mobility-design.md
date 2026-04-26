---
title: "Traffic-aware mobility (Ola/Uber-like motion) — design"
date: 2026-04-26
status: draft
---

## Goal

Make the map *feel like a real mobility product*:

- Vehicles (cars + bikes) **move place-to-place** along real Bangalore road geometry (already done).
- Motion is **traffic-aware** (slows in congestion, smooth near intersections, no teleporting).
- Routing is **dynamic** (periodic reroutes like Ola/Uber).
- EV charger choice is made by agents to **optimize city efficiency** (throughput, grid stress, queueing).
- Must remain **deterministic** (scenario + seed) for judge replayability and HF Spaces reliability.

Non-goals (for hackathon scope):

- Live third-party traffic APIs.
- Perfect physical simulation; we need “believable” not “perfect”.

## Current baseline (what exists)

- Frontend `MapView` animates vehicles along a polyline with a fixed speed scalar (m/s).
- Backend returns OSM road-following polylines for routing (`/demo/step` via `road_router`).
- Stations are displayed as icon layer; vehicles are car/bike icons with heading.
- Multi-agent “GridOperator vs FleetDispatcher” exists (role rewards + negotiation UI).

## Desired experience (user-facing)

- Roads show a subtle **traffic heat** (green → red) that updates over time.
- Vehicles **accelerate/decelerate** slightly and appear to “flow” with traffic.
- Every few ticks, you see a short “recalculating…” moment: route line updates and the vehicle turns onto a different corridor.
- Oracle visibly chooses **better chargers** under traffic + queues; baseline makes locally-greedy choices.

## Approach options

### Option A (recommended): Deterministic synthetic traffic field + periodic reroute

- Generate a per-edge traffic multiplier \(m \in [0.35, 1.15]\) each tick, deterministic from:
  - `scenario`, `seed`, `tick`, and stable edge id
  - plus a few moving “hotspots” (waves) that create believable congestion corridors
- Route cost uses:
  - base travel time (edge length / base speed by highway class)
  - multiplied by traffic multiplier
  - optional intersection penalty (small) to bias smoother routes
- Reroute cadence:
  - every **6 ticks**, with **deterministic** per-vehicle jitter in \(\{-1,0,+1\}\) computed as:
    - `jitter = hash32(seed, scenario, ev_id) % 3 - 1`
    - `reroute_tick = (tick % 6 == (3 + jitter))`
  - This MUST be stable across restarts and independent of vehicle iteration order.

Pros: reliable, easy to demo, no external deps, judge-friendly determinism.  
Cons: traffic is synthetic (but believable).

### Option B: Microscopic traffic sim (queue + signals)

- Add explicit intersections/signals and vehicle-vehicle interactions.

Pros: most realistic.  
Cons: expensive scope, hard to tune, can look buggy.

### Option C: Frontend-only “traffic illusion”

- Fake traffic by only changing vehicle speed (no reroute + no route cost impact).

Pros: minimal backend changes.  
Cons: not convincing; agents can’t optimize against it.

We choose **Option A**.

## System design

### API contract (authoritative, versioned)

All server step responses that include traffic-aware mobility MUST include:

- `tick`: int (monotonic sim tick)
- `tick_dt_s`: float (seconds per tick; constant per scenario)
- `schema_version`: string (e.g. `"traffic-v1"`)

**Route event (per `ev_id`)**

- `ev_id`: string
- `polyline`: array of `[lat, lng]` (WGS84). This matches current server behavior; the frontend converts to `[lng,lat]` for Deck rendering.
- `eta_s`: float (seconds; computed by server using the same edge weights used for routing at this `tick`)
- `reroute_reason`: string | null (one of: `"periodic"`, `"traffic_spike"`, `"queue_growth"`, `"grid_constraint"`)

**Traffic snapshot (`traffic`)** (used for rendering only; routing uses the same underlying model)

- `traffic.encoding`: string (one of: `"uv_mult_v1"`)
- `traffic.edges`: array of `{ u: int, v: int, m_q: int }` where:
  - `(u,v)` are road-graph node ids for the (undirected) edge
  - `m = m_q / 1000.0` and `m` is clamped to `[0.35, 1.15]`
  - `(u,v)` order is normalized by the server as `u <= v` to keep join keys stable.
- Frontend joins traffic to render geometry by matching `(u,v)` against render-edge metadata (see “Traffic overlay join” below).

### Data model

Add to server step outputs (demo + MA):

- `traffic`: a compact snapshot for rendering
  - **Encoding**: must follow `traffic.encoding="uv_mult_v1"` above
  - **Rate**: updated every tick (or every 2 ticks if perf needs)
- For each route event already returned:
  - include `eta_s` (estimated travel time along chosen route under current traffic)
  - include `reroute_reason` when a route changed (e.g. `"traffic_spike"`, `"queue_growth"`)

### Traffic generator (server)

Module: `ev_grid_oracle/traffic.py` (new)

- `TrafficModel(seed, scenario)` with:
  - `multiplier_for_edge(edge_id, tick) -> float`
  - deterministic moving hotspots:
    - 2–4 gaussian blobs in lat/lng space with time-varying center
    - projects to nearby edges using edge midpoint
- Guardrails:
  - clamp multipliers to \([0.35, 1.15]\)
  - stable across restarts for same seed/scenario

### Routing integration (server)

Module: `server/road_router.py` (existing)

- Extend shortest-path weight to:
  - \(w(u,v) = travel\_s(u,v) \cdot traffic(u,v,tick) + intersection\_penalty\)
- `travel_s(u,v)` is the precomputed base travel time already stored in the baked road graph (stable + deterministic).
- Optional follow-up (non-blocking): incorporate highway class and/or turn penalties into the graph build step to improve realism.

### Agent decision (GridOperator vs FleetDispatcher)

- **FleetDispatcher** proposes a charger plan per EV minimizing:
  - ETA to charger under traffic
  - expected queue wait at charger
  - battery risk constraints
- **GridOperator** applies grid constraints (feeder limits / stress) and may:
  - nudge EVs to alternate chargers
  - impose soft penalties for routing through feeder-hot corridors (scenario dependent)
- Negotiation protocol stays the same; we only change:
  - what evidence each agent uses (traffic + queues + feeder stress)
  - what’s logged (reroute reasons and ETA deltas)

### Frontend rendering + motion

Module: `web/src/map/MapView.ts` (existing)

- **Traffic overlay**:
  - additional `PathLayer` for roads with color based on traffic multiplier
  - subtle alpha so basemap stays readable
- **Vehicle speed**:
  - per-vehicle instantaneous speed = baseSpeedMps * trafficFactorAlongRoute
  - apply smoothing (exponential moving average) so speed changes aren’t jarring
- **Intersection easing**:
  - reduce speed slightly when heading change exceeds a threshold (simulated turns)
- **Reroute**:
  - when new event for same `ev_id` arrives with a different polyline, replace route
  - briefly pulse route layer and show a tiny “recalculating…” badge near vehicle (optional)

### Traffic overlay join (render ↔ router)

To render traffic on roads, the frontend needs a stable key to join server `traffic.edges` to drawn road segments.

We will extend the render-optimized road asset build (`tools/build_roads_render.py`) to emit **render edges**:

- new artifact: `web/public/maps/bangalore_roads_edges_render.json`
- shape: array of `{ u: int, v: int, highway: string, path: [[lng,lat], ...] }`
- `(u,v)` correspond to the **same** road-graph node ids used by the router graph file.
- frontend:
  - renders traffic overlay from this file
  - uses `(min(u,v), max(u,v))` as join key to `traffic.edges`

## Performance + stability

- Must handle **100–500 vehicles**:
  - keep current vehicle cap + TTL logic (clean map)
  - avoid rebuilding static layers every frame
- Traffic payload + render stability:
  - **Traffic payload budget**: `traffic` MUST be ≤ **200 KB per tick** at 500 vehicles. If exceeded, server MUST fall back to updating every 2 ticks and/or sending only edges near active vehicles’ route corridors.
  - **Spatial filtering rule**: server sends traffic only for edges whose midpoint is within **R meters** (configurable; default 750m) of any active vehicle position or any point along its current route polyline (sampled).
  - **Client caching**: frontend MUST treat missing edges as `m = 1.0` and cache the last received multiplier per `edge_id` until replaced (to avoid flicker).
- HF Spaces:
  - no external traffic APIs
  - deterministic simulation for reproducible demos

Backward compatibility:

- During rollout, `schema_version`, `tick_dt_s`, and `traffic` are **additive** fields for `/demo/step` and `/ma/step`.
- UI should treat them as optional until both server + client are deployed.

## Test plan

- Unit test: traffic multipliers deterministic for same seed/scenario/tick.
- Unit test: routing weight changes when traffic spikes (path should change on controlled graph).
- Smoke test: demo step returns `traffic` and route events include `eta_s`.
- Visual sanity:
  - traffic overlay visible
  - vehicle speed changes are noticeable but not chaotic
  - reroute occurs every ~6 ticks and is logged

## Acceptance criteria (what “done” means)

- You can watch a car:
  - move continuously along roads,
  - slow down in red corridors,
  - reroute onto greener corridors within 6–7 ticks,
  - and arrive at a charger chosen by the agents.
- Baseline vs Oracle difference is legible in < 3 seconds:
  - Oracle reduces ETA + queueing + grid stress under the same traffic field.

