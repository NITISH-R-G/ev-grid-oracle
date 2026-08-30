# Documentation for `server/app.py`

## Classes

### Class `DemoNewRequest`

No documentation provided.

### Class `MANewRequest`

No documentation provided.

### Class `MAAutoStepRequest`

No documentation provided.

### Class `DemoSpawnVehicleRequest`

No documentation provided.

## Functions

### Function `_request_id`

No documentation provided.

### Function `_oracle_skip_llm_env`

No documentation provided.

### Function `_rate_limit`

No documentation provided.

### Function `_demo_oracle_act_with_guard`

Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle__timed_out, oracle__skipped_env

### Function `root`

No documentation provided.

### Function `healthz`

HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

### Function `_osm_route_polyline`

No documentation provided.

### Function `_graph_route_polyline`

Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

### Function `_spawn_road_point_away_from_stations`

Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

### Function `_demo_session_gc`

No documentation provided.

### Function `_demo_session_get`

No documentation provided.

### Function `_ma_gc`

No documentation provided.

### Function `_ma_get`

No documentation provided.

### Function `ma_new`

No documentation provided.

### Function `_grid_policy`

No documentation provided.

### Function `ma_auto_step`

No documentation provided.

### Function `ma_state`

No documentation provided.

### Function `ma_step`

No documentation provided.

### Function `_obs_to_jsonable`

No documentation provided.

### Function `_station_nodes`

No documentation provided.

### Function `demo_new`

No documentation provided.

### Function `demo_state`

No documentation provided.

### Function `demo_spawn_vehicle`

Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

### Function `demo_step`

No documentation provided.

### Function `main`

No documentation provided.

### Function `run`

No documentation provided.
