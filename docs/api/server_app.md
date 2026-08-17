# Documentation for ./server/app.py

### _demo_oracle_act_with_guard

Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

### healthz

HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

### _graph_route_polyline

Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

### _spawn_road_point_away_from_stations

Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

### demo_spawn_vehicle

Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.
