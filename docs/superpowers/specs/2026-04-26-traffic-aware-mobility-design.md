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
  - every **6 ticks**, with per-vehicle jitter \(\pm 1\) tick to avoid robotic sync

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

### Data model

Add to server step outputs (demo + MA):

- `traffic`: a compact snapshot for rendering
  - **Shape**: list of `{ u: int, v: int, m: float }` or a packed dict keyed by edge id
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
  - \(w(u,v) = base\_time(u,v) \cdot traffic(u,v,tick) + intersection\_penalty\)
- Base time derived from:
  - edge length meters / speed_by_highway_mps
  - speed table: motorway/trunk/primary/secondary/tertiary/residential

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

## Performance + stability

- Must handle **100–500 vehicles**:
  - keep current vehicle cap + TTL logic (clean map)
  - avoid rebuilding static layers every frame
- HF Spaces:
  - no external traffic APIs
  - deterministic simulation for reproducible demos

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

