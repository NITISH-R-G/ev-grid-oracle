# API Reference for `./server/app.py`

## Function: `_request_id`

No docstring available.

## Function: `_oracle_skip_llm_env`

No docstring available.

## Function: `_rate_limit`

No docstring available.

## Function: `_demo_oracle_act_with_guard`

Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

## Function: `root`

No docstring available.

## Function: `healthz`

HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

## Function: `_osm_route_polyline`

No docstring available.

## Function: `_graph_route_polyline`

Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

## Function: `_spawn_road_point_away_from_stations`

Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

## Function: `_demo_session_gc`

No docstring available.

## Function: `_demo_session_get`

No docstring available.

## Class: `DemoNewRequest`

No docstring available.

## Function: `_ma_gc`

No docstring available.

## Function: `_ma_get`

No docstring available.

## Class: `MANewRequest`

No docstring available.

## Function: `ma_new`

No docstring available.

## Function: `_grid_policy`

No docstring available.

## Class: `MAAutoStepRequest`

No docstring available.

## Function: `ma_auto_step`

No docstring available.

## Function: `ma_state`

No docstring available.

## Function: `ma_step`

No docstring available.

## Function: `_obs_to_jsonable`

No docstring available.

## Function: `_station_nodes`

No docstring available.

## Function: `demo_new`

No docstring available.

## Function: `demo_state`

No docstring available.

## Class: `DemoSpawnVehicleRequest`

No docstring available.

## Function: `demo_spawn_vehicle`

Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

## Function: `demo_step`

No docstring available.

## Function: `main`

No docstring available.

## Function: `run`

No docstring available.
