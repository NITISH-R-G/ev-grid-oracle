# Documentation for `server/app.py`

## Function: `_request_id`

## Function: `_oracle_skip_llm_env`

## Function: `_rate_limit`

## Function: `_demo_oracle_act_with_guard`

Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

## Function: `root`

## Function: `healthz`

HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

## Function: `_osm_route_polyline`

## Function: `_graph_route_polyline`

Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

## Function: `_spawn_road_point_away_from_stations`

Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

## Function: `_demo_session_gc`

## Function: `_demo_session_get`

## Class: `DemoNewRequest`

## Function: `_ma_gc`

## Function: `_ma_get`

## Class: `MANewRequest`

## Function: `ma_new`

## Function: `_grid_policy`

## Class: `MAAutoStepRequest`

## Function: `ma_auto_step`

## Function: `ma_state`

## Function: `ma_step`

## Function: `_obs_to_jsonable`

## Function: `_station_nodes`

## Function: `demo_new`

## Function: `demo_state`

## Class: `DemoSpawnVehicleRequest`

## Function: `demo_spawn_vehicle`

Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

## Function: `demo_step`

## Function: `main`

## Function: `run`
