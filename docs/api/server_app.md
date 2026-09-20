# Module: `./server/app.py`

**Description:**
*No module docstring provided.*

## Function: `_request_id`
*No function docstring provided.*

## Function: `_oracle_skip_llm_env`
*No function docstring provided.*

## Function: `_rate_limit`
*No function docstring provided.*

## Function: `_demo_oracle_act_with_guard`
Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

## Function: `root`
*No function docstring provided.*

## Function: `healthz`
HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

## Function: `_osm_route_polyline`
*No function docstring provided.*

## Function: `_graph_route_polyline`
Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

## Function: `_spawn_road_point_away_from_stations`
Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

## Function: `_demo_session_gc`
*No function docstring provided.*

## Function: `_demo_session_get`
*No function docstring provided.*

## Class: `DemoNewRequest`
*No class docstring provided.*

## Function: `_ma_gc`
*No function docstring provided.*

## Function: `_ma_get`
*No function docstring provided.*

## Class: `MANewRequest`
*No class docstring provided.*

## Function: `ma_new`
*No function docstring provided.*

## Function: `_grid_policy`
*No function docstring provided.*

## Class: `MAAutoStepRequest`
*No class docstring provided.*

## Function: `ma_auto_step`
*No function docstring provided.*

## Function: `ma_state`
*No function docstring provided.*

## Function: `ma_step`
*No function docstring provided.*

## Function: `_obs_to_jsonable`
*No function docstring provided.*

## Function: `_station_nodes`
*No function docstring provided.*

## Function: `demo_new`
*No function docstring provided.*

## Function: `demo_state`
*No function docstring provided.*

## Class: `DemoSpawnVehicleRequest`
*No class docstring provided.*

## Function: `demo_spawn_vehicle`
Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

## Function: `demo_step`
*No function docstring provided.*

## Function: `main`
*No function docstring provided.*

