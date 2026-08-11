# Documentation for `./server/app.py`

## Classes

### DemoNewRequest

### MANewRequest

### MAAutoStepRequest

### DemoSpawnVehicleRequest

## Functions

### _request_id

### _oracle_skip_llm_env

### _rate_limit

### _demo_oracle_act_with_guard
Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

### root

### healthz
HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

### _osm_route_polyline

### _graph_route_polyline
Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

### _spawn_road_point_away_from_stations
Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

### _demo_session_gc

### _demo_session_get

### _ma_gc

### _ma_get

### ma_new

### _grid_policy

### ma_auto_step

### ma_state

### ma_step

### _obs_to_jsonable

### _station_nodes

### demo_new

### demo_state

### demo_spawn_vehicle
Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

### demo_step

### main
