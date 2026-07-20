# API Reference

## File: `./test_script.py`

### Class: `ChargerType`

### Class: `StationState`

## File: `./test_memory.py`

## File: `./training/fair_eval.py`

### Function: `_binom_two_sided_exact_p`

Two-sided exact test for Binomial(n, p); used for McNemar discordant pairs (p=0.5).

### Function: `mcnemar_discordant`

McNemar on paired binary outcomes.
b01 = count(baseline True, oracle False); b10 = count(baseline False, oracle True).

### Function: `paired_mcnemar_analysis`

Paired McNemar for headline binaries (same rows as Wilson chart).

### Function: `wilson_interval`

Wilson score interval for a binomial proportion.
Returns (low, high, p_hat). For n==0 returns (nan, nan, nan).

### Function: `_binary_keys`

### Function: `analyze_per_episode`

### Function: `_paired_improvement_counts`

Operational 'wins' where oracle strictly improves a binary bad outcome vs baseline.

### Function: `plot_fair_eval`

Bar chart: select headline baseline vs oracle binary rates with Wilson error bars.

### Function: `main`

## File: `./training/make_plots.py`

### Function: `_boxplot_compat`

### Function: `_per_episode_rows`

### Function: `plot_kpi_bars`

### Function: `plot_episode_trajectories`

### Function: `plot_delta_histograms`

### Function: `plot_reward_breakdown`

### Function: `plot_boxplots`

### Function: `plot_oracle_win_rates`

### Function: `plot_paired_scatter`

### Function: `plot_binary_timeline`

### Function: `plot_fair_eval_rates`

### Function: `plot_mcnemar_summary`

### Function: `plot_dashboard_grid`

### Function: `main`

## File: `./training/evaluate.py`

### Class: `EpisodeMetrics`

### Function: `_episode_metrics_to_json`

### Function: `run_episode`

### Function: `summarize`

### Function: `summarize_reward_breakdown`

### Function: `main`

## File: `./training/__init__.py`

## File: `./tools/road_reward_smoke.py`

### Function: `main`

## File: `./tools/fetch_osm_roads.py`

### Class: `BBox`

### Function: `_fetch_overpass`

### Function: `_simplify_line`

### Function: `_to_feature_collection`

### Function: `build_query`

### Function: `main`

## File: `./tools/build_road_graph.py`

### Function: `haversine_m`

### Function: `_encode_signed`

### Function: `encode_polyline_latlng`

Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

### Function: `speed_kmh`

### Class: `Node`

### Function: `snap`

### Function: `_coords_latlng_from_geojson_line`

### Function: `parse_args`

### Function: `build_adjacency`

Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

### Function: `contract_edges`

Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

### Function: `filter_largest_component`

Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.

### Function: `main`

## File: `./tools/docs_sync.py`

### Function: `extract_docs`

## File: `./tools/export_grpo_tensorboard_plots.py`

### Function: `_pick_tags`

### Function: `main`

## File: `./tools/write_eval_snapshot.py`

### Function: `main`

## File: `./tools/generate_health_dashboard.py`

### Function: `run_cmd`

### Function: `get_git_stats`

### Function: `get_leaderboard`

### Function: `get_documentation_health`

### Function: `fetch_github_stats`

### Function: `run_pytest_cov`

### Function: `run_radon`

### Function: `run_bandit`

### Function: `run_ruff`

### Function: `calculate_health_scores`

### Function: `generate_ai_insights`

### Function: `main`

## File: `./tools/prune_osm_geojson.py`

### Function: `_pad_bbox`

### Function: `_line_intersects_bbox`

### Function: `_simplify_uniform`

### Function: `main`

## File: `./tools/generate_knowledge_graph.py`

### Function: `generate_knowledge_graph`

## File: `./tools/build_roads_render.py`

### Function: `main`

## File: `./tools/fetch_bangalore_roads_overpass.py`

### Function: `_chunk`

### Function: `_overpass_query`

### Function: `_tile_bbox`

### Function: `_http_post`

### Function: `_to_geojson`

### Function: `main`

## File: `./tools/sync_space_to_hub.py`

### Function: `main`

## File: `./tools/__init__.py`

## File: `./viz/city_map.py`

### Function: `_station_color`

### Function: `_norm`

### Class: `RenderConfig`

### Class: `CityMapRenderer`

### Function: `run_live`

## File: `./viz/gradio_demo.py`

### Function: `_norm`

### Function: `_station_color`

### Function: `render_map`

### Class: `Session`

### Function: `new_session`

### Function: `step_once`

### Function: `compute_kpis`

## File: `./viz/record.py`

### Function: `record`

Record frames as PNGs.

- `tick_every_frames`: how many frames to show per env.step() (slows animation, looks smoother).

### Function: `main`

## File: `./viz/record_two_phase.py`

### Function: `_step_action`

### Function: `record_phase`

### Function: `main`

## File: `./viz/__init__.py`

## File: `./ev_grid_oracle/bescom_feed.py`

### Class: `BESCOMFeedAPI`

Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.

## File: `./ev_grid_oracle/city_graph.py`

### Class: `StationSpec`

### Function: `get_station_by_id`

### Function: `get_station_by_slug`

### Function: `haversine_km`

### Function: `_edge_minutes`

### Function: `_add_chain_edges`

### Function: `_add_dense_within_cluster`

### Function: `build_city_graph`

### Function: `travel_time_minutes`

### Function: `nearest_stations_by_geo`

## File: `./ev_grid_oracle/traffic.py`

### Function: `_clamp`

### Function: `_stable_u01`

Stable pseudo-random in [0,1) from input parts.
Deterministic across processes and Python versions.

### Class: `TrafficModel`

Deterministic synthetic traffic for hackathon demos.

Returns a multiplier m in [0.35, 1.15] to scale base travel_s on an edge.

## File: `./ev_grid_oracle/env.py`

### Class: `EVGridCore`

Core env logic (no HTTP). Server wraps this.

v0 slice: deterministic schema, minimal dynamics.
Next slices add demand_sim/grid_sim/reward engine.

### Function: `_peak_risk`

### Function: `_make_ev`

### Function: `_apply_action`

### Function: `_drain_queues_and_charging`

### Function: `_update_station_waits`

### Function: `_build_prompt`

## File: `./ev_grid_oracle/world_model_verifier.py`

### Class: `PredictionScore`

### Function: `_top3`

### Function: `rollout_deterministic_5ticks`

Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
This is intentionally verifier-friendly (stable + reproducible) for RLVR.

### Function: `score_prediction`

Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].

## File: `./ev_grid_oracle/multi_agent.py`

### Class: `MultiAgentSession`

Minimal explicit multi-agent wrapper around EVGridCore.

- GridOperator emits a directive (constraint signal) + optional message.
- FleetDispatcher emits an action + optional message.
- Resolver applies directive deterministically and steps EVGridCore.

## File: `./ev_grid_oracle/road_models.py`

### Class: `RoadAction`

Minimal action space for RL on a real road graph:
choose the next connected node (no teleportation).

### Class: `RoadState`

### Class: `RoadObservation`

## File: `./ev_grid_oracle/road_env.py`

### Class: `RoadCore`

## File: `./ev_grid_oracle/demand_sim.py`

### Class: `DemandParams`

### Function: `_gaussian_bump`

### Function: `expected_arrivals_per_step`

### Function: `sample_arrivals_per_step`

## File: `./ev_grid_oracle/reward_hack.py`

### Class: `RewardHackDetector`

Stateful, deterministic detector for common reward-hacking patterns.

Goal: give the existing anti-hack flags "teeth" by detecting multi-step
exploit patterns, not just single-step invalidity.

## File: `./ev_grid_oracle/policies.py`

### Function: `baseline_policy`

Greedy baseline: pick station minimizing (travel_time + wait + stress + price), avoid full.

Deterministic given state.

### Function: `always_defer_policy`

Collapse baseline: always defer (reward-hack / fairness stressor).

### Function: `always_load_shift_policy`

Collapse baseline: always load_shift on head EV (ignores queues / grid).

### Function: `nearest_travel_only_policy`

Collapse baseline: minimize travel time only (ignores price, wait, stress).
Used to show greedy multi-objective baseline is not trivially dominated.

## File: `./ev_grid_oracle/personas.py`

### Class: `PersonaParams`

### Function: `choose_persona`

## File: `./ev_grid_oracle/oracle_agent.py`

### Class: `OracleRuntime`

Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

### Class: `OracleAgent`

Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

## File: `./ev_grid_oracle/parsing.py`

### Function: `parse_simulation`

### Function: `parse_action`

### Function: `parse_simulation_and_action`

Parse both dream prediction and action (either can be missing).

## File: `./ev_grid_oracle/reward.py`

### Class: `RewardWeights`

### Function: `_haversine_km`

### Function: `_graph_route_km`

Approximate driving distance along the city graph using haversine edge weights.
Returns None if no path exists.

### Function: `compute_reward`

Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.

### Function: `split_role_rewards`

Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.

## File: `./ev_grid_oracle/scenarios.py`

### Class: `ScenarioEvent`

### Class: `ScenarioModifiers`

Lightweight knobs applied on top of the core simulator.
These are intentionally simple and deterministic for replayable judging.

### Function: `scenario_schedule`

Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

Note: ticks are env steps (5-minute increments by default).

### Function: `apply_scenario_events`

Returns updated modifiers and the list of events that fired this tick.

## File: `./ev_grid_oracle/models.py`

### Class: `ChargerType`

### Class: `ChargeRate`

### Class: `ActionType`

### Class: `DayType`

### Class: `PeakRisk`

### Class: `StationState`

### Class: `EVRequest`

### Class: `BESCOMFeederState`

Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### Class: `GridState`

### Class: `EVGridAction`

### Class: `EVGridObservation`

### Class: `NegotiationMessage`

A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### Class: `GridDirective`

GridOperator -> FleetDispatcher constraint signal (verifiable).

### Class: `MultiAgentStepRequest`

### Class: `MultiAgentStepResponse`

### Class: `SimTopStation`

### Class: `SimulationPrediction`

Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

### Function: `to_jsonable`

## File: `./ev_grid_oracle/grid_sim.py`

### Class: `GridParams`

### Function: `_clamp01`

### Function: `baseline_grid_load`

### Function: `renewable_pct`

### Function: `update_grid_load`

## File: `./ev_grid_oracle/__init__.py`

## File: `./server/role_metrics.py`

### Function: `compute_role_kpis`

### Function: `compute_role_reward_breakdown`

Lightweight, explainable credit assignment for demo storytelling.

This is NOT a full MARL credit assignment — it allocates the *same* component
values across roles with fixed weights so totals remain easy to interpret.

### Function: `_peak_risk_score`

### Function: `summarize_action`

## File: `./server/road_router.py`

### Function: `haversine_m`

### Function: `decode_polyline_latlng`

### Class: `RoadRouter`

### Function: `get_router`

## File: `./server/app.py`

### Function: `_request_id`

### Function: `_oracle_skip_llm_env`

### Function: `_rate_limit`

### Function: `_demo_oracle_act_with_guard`

Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

### Function: `root`

### Function: `healthz`

HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

### Function: `_osm_route_polyline`

### Function: `_graph_route_polyline`

Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

### Function: `_spawn_road_point_away_from_stations`

Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

### Function: `_demo_session_gc`

### Function: `_demo_session_get`

### Class: `DemoNewRequest`

### Function: `_ma_gc`

### Function: `_ma_get`

### Class: `MANewRequest`

### Function: `ma_new`

### Function: `_grid_policy`

### Class: `MAAutoStepRequest`

### Function: `ma_auto_step`

### Function: `ma_state`

### Function: `ma_step`

### Function: `_obs_to_jsonable`

### Function: `_station_nodes`

### Function: `demo_new`

### Function: `demo_state`

### Class: `DemoSpawnVehicleRequest`

### Function: `demo_spawn_vehicle`

Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

### Function: `demo_step`

### Function: `main`

## File: `./server/ev_grid_road_environment.py`

### Class: `EVGridRoadEnvironment`

Separate OpenEnv environment that forces real-road-graph actions.
Mounted as a sub-app under /road/ so it doesn't break the existing env.

## File: `./server/ev_grid_environment.py`

### Class: `EVGridEnvironment`

## File: `./server/__init__.py`

## File: `./tests/test_demo_api.py`

### Function: `test_demo_new_and_step_roundtrip`

### Function: `test_demo_spawn_vehicle_route_event`

### Function: `test_demo_step_forced_action_validation_422`

### Function: `test_health_shape`

### Function: `test_demo_sessions_ttl_eviction`

### Function: `test_ma_new_and_step_roundtrip`

## File: `./tests/test_env_determinism.py`

### Function: `test_reset_state_identical_two_cores_same_seed`

### Function: `test_step_sequence_identical_two_cores_same_actions`

### Function: `test_ev_grid_action_rejects_malformed_payload`

### Function: `test_route_action_requires_station`

## File: `./tests/test_parsing.py`

### Function: `test_parse_simulation_valid`

### Function: `test_parse_simulation_missing_match`

### Function: `test_parse_simulation_exception_handling`

## File: `./tests/test_policies_collapse.py`

### Function: `_run_policy`

### Function: `test_collapse_policies_do_not_crash`

### Function: `test_collapse_policies_return_valid_actions_when_pending`

## File: `./tests/test_evaluate_paired.py`

### Function: `_chdir_repo_root`

### Function: `test_baseline_rollout_identical_for_same_seed_and_scenario`

### Function: `test_oracle_matches_baseline_when_skip_llm`

### Function: `test_evaluate_cli_paired_json`

### Function: `test_fair_eval_cli`

## File: `./tests/test_reward.py`

### Function: `test_reward_breakdown_has_keys_and_total`

### Function: `test_deferring_critical_ev_penalized`

### Function: `test_invalid_station_routes_penalized`

### Function: `test_split_role_rewards_exception_handling`

## File: `./tests/test_models_and_graph.py`

### Function: `test_city_graph_connected_and_25_stations`

### Function: `test_action_route_requires_station_id_and_zero_defer`

### Function: `test_action_defer_requires_positive_defer_minutes`

### Function: `test_time_advances_with_5min_steps`

## File: `./tests/test_world_model_verifier.py`

### Function: `test_rollout_deterministic_is_stable`

### Function: `test_prediction_score_higher_when_close`

## File: `./tests/test_fair_eval_mcnemar.py`

### Function: `test_mcnemar_no_discordant_is_neutral`

### Function: `test_mcnemar_strong_asymmetry_low_p`

### Function: `test_paired_mcnemar_analysis_shape`

## File: `./tests/__init__.py`
