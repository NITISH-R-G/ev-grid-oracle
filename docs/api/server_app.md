# Documentation for `./server/app.py`

## Classes

### `DemoNewRequest`
*No docstring available.*

### `MANewRequest`
*No docstring available.*

### `MAAutoStepRequest`
*No docstring available.*

### `DemoSpawnVehicleRequest`
*No docstring available.*

## Functions

### `_request_id`
*No docstring available.*

### `_oracle_skip_llm_env`
*No docstring available.*

### `_rate_limit`
*No docstring available.*

### `_demo_oracle_act_with_guard`
Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

### `root`
*No docstring available.*

### `healthz`
HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

### `_osm_route_polyline`
*No docstring available.*

### `_graph_route_polyline`
Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

### `_spawn_road_point_away_from_stations`
Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

### `_demo_session_gc`
*No docstring available.*

### `_demo_session_get`
*No docstring available.*

### `_ma_gc`
*No docstring available.*

### `_ma_get`
*No docstring available.*

### `ma_new`
*No docstring available.*

### `_grid_policy`
*No docstring available.*

### `ma_auto_step`
*No docstring available.*

### `ma_state`
*No docstring available.*

### `ma_step`
*No docstring available.*

### `_obs_to_jsonable`
*No docstring available.*

### `_station_nodes`
*No docstring available.*

### `demo_new`
*No docstring available.*

### `demo_state`
*No docstring available.*

### `demo_spawn_vehicle`
Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

### `demo_step`
*No docstring available.*

### `main`
*No docstring available.*

### `run`
*No docstring available.*
