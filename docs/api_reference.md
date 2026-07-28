# API Reference

This is an auto-generated API reference.

## ./test_script.py

### Class: `ChargerType`

### Class: `StationState`

## ./ev_grid_oracle/bescom_feed.py

### Class: `BESCOMFeedAPI`

Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.

### Function: `snapshot`

## ./ev_grid_oracle/city_graph.py

### Class: `StationSpec`

### Function: `get_station_by_id`

### Function: `get_station_by_slug`

### Function: `haversine_km`

### Function: `build_city_graph`

### Function: `travel_time_minutes`

### Function: `nearest_stations_by_geo`

## ./ev_grid_oracle/demand_sim.py

### Class: `DemandParams`

### Function: `expected_arrivals_per_step`

### Function: `sample_arrivals_per_step`

## ./ev_grid_oracle/env.py

### Class: `EVGridCore`

Core env logic (no HTTP). Server wraps this.

v0 slice: deterministic schema, minimal dynamics.
Next slices add demand_sim/grid_sim/reward engine.

### Function: `reset`

### Function: `step`

## ./ev_grid_oracle/grid_sim.py

### Class: `GridParams`

### Function: `baseline_grid_load`

### Function: `renewable_pct`

### Function: `update_grid_load`

## ./ev_grid_oracle/models.py

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

## ./ev_grid_oracle/multi_agent.py

### Class: `MultiAgentSession`

Minimal explicit multi-agent wrapper around EVGridCore.

- GridOperator emits a directive (constraint signal) + optional message.
- FleetDispatcher emits an action + optional message.
- Resolver applies directive deterministically and steps EVGridCore.

### Function: `step`

### Function: `snapshot`

Read-only view of the underlying core state.

## ./ev_grid_oracle/oracle_agent.py

### Class: `OracleRuntime`

Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

### Class: `OracleAgent`

Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

### Function: `load`

### Function: `act`

### Function: `act_with_text`

### Function: `is_active`

## ./ev_grid_oracle/parsing.py

### Function: `parse_simulation`

### Function: `parse_action`

### Function: `parse_simulation_and_action`

Parse both dream prediction and action (either can be missing).

## ./ev_grid_oracle/personas.py

### Class: `PersonaParams`

### Function: `choose_persona`

## ./ev_grid_oracle/policies.py

### Function: `baseline_policy`

Greedy baseline: pick station minimizing (travel_time + wait + stress + price), avoid full.  # noqa: E501

Deterministic given state.

### Function: `always_defer_policy`

Collapse baseline: always defer (reward-hack / fairness stressor).

### Function: `always_load_shift_policy`

Collapse baseline: always load_shift on head EV (ignores queues / grid).

### Function: `nearest_travel_only_policy`

Collapse baseline: minimize travel time only (ignores price, wait, stress).
Used to show greedy multi-objective baseline is not trivially dominated.

## ./ev_grid_oracle/reward.py

### Class: `RewardWeights`

### Function: `compute_reward`

Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.

### Function: `split_role_rewards`

Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.

### Function: `add_flag`

### Function: `f`

## ./ev_grid_oracle/reward_hack.py

### Class: `RewardHackDetector`

Stateful, deterministic detector for common reward-hacking patterns.

Goal: give the existing anti-hack flags "teeth" by detecting multi-step
exploit patterns, not just single-step invalidity.

### Function: `reset`

### Function: `step`

### Function: `add`

## ./ev_grid_oracle/road_env.py

### Class: `RoadCore`

### Function: `reset`

### Function: `step`

## ./ev_grid_oracle/road_models.py

### Class: `RoadAction`

Minimal action space for RL on a real road graph:
choose the next connected node (no teleportation).

### Class: `RoadState`

### Class: `RoadObservation`

## ./ev_grid_oracle/scenarios.py

### Class: `ScenarioEvent`

### Class: `ScenarioModifiers`

Lightweight knobs applied on top of the core simulator.
These are intentionally simple and deterministic for replayable judging.

### Function: `scenario_schedule`

Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

Note: ticks are env steps (5-minute increments by default).

### Function: `apply_scenario_events`

Returns updated modifiers and the list of events that fired this tick.

## ./ev_grid_oracle/traffic.py

### Class: `TrafficModel`

Deterministic synthetic traffic for hackathon demos.

Returns a multiplier m in [0.35, 1.15] to scale base travel_s on an edge.

### Function: `multiplier_for_edge`

### Function: `hotspot`

## ./ev_grid_oracle/world_model_verifier.py

### Class: `PredictionScore`

### Function: `rollout_deterministic_5ticks`

Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.  # noqa: E501
This is intentionally verifier-friendly (stable + reproducible) for RLVR.

### Function: `score_prediction`

Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].

## ./server/app.py

### Function: `root`

### Function: `healthz`

HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

### Class: `DemoNewRequest`

### Class: `MANewRequest`

### Function: `ma_new`

### Class: `MAAutoStepRequest`

### Function: `ma_auto_step`

### Function: `ma_state`

### Function: `ma_step`

### Function: `demo_new`

### Function: `demo_state`

### Class: `DemoSpawnVehicleRequest`

### Function: `demo_spawn_vehicle`

Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

### Function: `demo_step`

### Function: `main`

### Function: `run`

## ./server/ev_grid_environment.py

### Class: `EVGridEnvironment`

### Function: `reset`

### Function: `step`

### Function: `state`

## ./server/ev_grid_road_environment.py

### Class: `EVGridRoadEnvironment`

Separate OpenEnv environment that forces real-road-graph actions.
Mounted as a sub-app under /road/ so it doesn't break the existing env.

### Function: `reset`

### Function: `step`

### Function: `state`

## ./server/road_router.py

### Function: `haversine_m`

### Function: `decode_polyline_latlng`

### Class: `RoadRouter`

### Function: `get_router`

### Function: `load`

### Function: `nearest_node`

### Function: `route_polyline`

## ./server/role_metrics.py

### Function: `compute_role_kpis`

### Function: `compute_role_reward_breakdown`

Lightweight, explainable credit assignment for demo storytelling.

This is NOT a full MARL credit assignment — it allocates the *same* component
values across roles with fixed weights so totals remain easy to interpret.

### Function: `summarize_action`

### Function: `part`

## ./tests/test_demo_api.py

### Function: `test_demo_new_and_step_roundtrip`

### Function: `test_demo_spawn_vehicle_route_event`

### Function: `test_demo_step_forced_action_validation_422`

### Function: `test_health_shape`

### Function: `test_demo_sessions_ttl_eviction`

### Function: `test_ma_new_and_step_roundtrip`

## ./tests/test_env_determinism.py

Determinism + strict action validation (core env, no LLM).

### Function: `test_reset_state_identical_two_cores_same_seed`

### Function: `test_step_sequence_identical_two_cores_same_actions`

### Function: `test_ev_grid_action_rejects_malformed_payload`

### Function: `test_route_action_requires_station`

## ./tests/test_evaluate_paired.py

### Function: `test_baseline_rollout_identical_for_same_seed_and_scenario`

### Function: `test_oracle_matches_baseline_when_skip_llm`

### Function: `test_evaluate_cli_paired_json`

### Function: `test_fair_eval_cli`

## ./tests/test_fair_eval_mcnemar.py

### Function: `test_mcnemar_no_discordant_is_neutral`

### Function: `test_mcnemar_strong_asymmetry_low_p`

### Function: `test_paired_mcnemar_analysis_shape`

## ./tests/test_models_and_graph.py

### Function: `test_city_graph_connected_and_25_stations`

### Function: `test_action_route_requires_station_id_and_zero_defer`

### Function: `test_action_defer_requires_positive_defer_minutes`

### Function: `test_time_advances_with_5min_steps`

## ./tests/test_parsing.py

### Function: `test_parse_simulation_valid`

### Function: `test_parse_simulation_missing_match`

### Function: `test_parse_simulation_exception_handling`

## ./tests/test_policies_collapse.py

Smoke tests for collapse / stressor policies (deterministic, no env crashes).

### Function: `test_collapse_policies_do_not_crash`

### Function: `test_collapse_policies_return_valid_actions_when_pending`

## ./tests/test_reward.py

### Function: `test_reward_breakdown_has_keys_and_total`

### Function: `test_deferring_critical_ev_penalized`

### Function: `test_invalid_station_routes_penalized`

### Function: `test_split_role_rewards_exception_handling`

## ./tests/test_world_model_verifier.py

### Function: `test_rollout_deterministic_is_stable`

### Function: `test_prediction_score_higher_when_close`

## ./tools/build_road_graph.py

### Function: `haversine_m`

### Function: `encode_polyline_latlng`

Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

### Function: `speed_kmh`

### Class: `Node`

### Function: `snap`

### Function: `parse_args`

### Function: `build_adjacency`

Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

### Function: `contract_edges`

Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

### Function: `filter_largest_component`

Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.

### Function: `main`

### Function: `add_neighbor`

### Function: `get_node`

### Function: `flush`

## ./tools/build_roads_render.py

### Function: `main`

## ./tools/docs_sync.py

### Function: `parse_file_for_docs`

### Function: `main`

## ./tools/export_grpo_tensorboard_plots.py

Export loss + reward (or closest TRL scalar tags) from a TensorBoard run dir into PNGs.

Hackathon requirement: committed plots from a *real* GRPO run. After `trainer.train()` in  # noqa: E501
`training/train_grpo.ipynb`, copy `ev_oracle_grpo_road/` from Colab (or run locally), then:  # noqa: E501

  pip install tensorboard matplotlib
  python tools/export_grpo_tensorboard_plots.py --logdir ev_oracle_grpo_road --out-dir artifacts  # noqa: E501

Writes e.g. artifacts/grpo_loss.png and artifacts/grpo_reward.png (filenames depend on tags found).  # noqa: E501

### Function: `main`

### Function: `plot_tag`

## ./tools/fetch_bangalore_roads_overpass.py

### Function: `main`

## ./tools/fetch_osm_roads.py

### Class: `BBox`

### Function: `build_query`

### Function: `main`

## ./tools/generate_health_dashboard.py

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

## ./tools/generate_knowledge_graph.py

### Function: `parse_file`

### Function: `main`

## ./tools/prune_osm_geojson.py

### Function: `main`

## ./tools/road_reward_smoke.py

### Function: `main`

### Function: `parse`

### Function: `reward`

## ./tools/sync_space_to_hub.py

Push this repo to a Hugging Face *Space* without using `git push` (avoids Hub binary rejections).  # noqa: E501

Docker Spaces often have **no** “link GitHub repo” in Settings — the Space is its own Hub git repo.  # noqa: E501
Use this script after `git push origin main`; it uploads sources + a fresh `web/dist` via the Hub API.  # noqa: E501

Usage:
  cd repo root
  npm --prefix web run build    # or let this script run it (default)
  python tools/sync_space_to_hub.py

Requires: `pip install huggingface_hub`, token with write access (`HF_TOKEN` or `huggingface-cli login`).  # noqa: E501

### Function: `main`

## ./tools/write_eval_snapshot.py

Run a tiny paired evaluate.py job and write artifacts/eval_snapshot.json (no LLM).

### Function: `main`

## ./training/evaluate.py

### Class: `EpisodeMetrics`

### Function: `run_episode`

### Function: `summarize`

### Function: `summarize_reward_breakdown`

### Function: `main`

## ./training/fair_eval.py

### Function: `mcnemar_discordant`

McNemar on paired binary outcomes.
b01 = count(baseline True, oracle False); b10 = count(baseline False, oracle True).

### Function: `paired_mcnemar_analysis`

Paired McNemar for headline binaries (same rows as Wilson chart).

### Function: `wilson_interval`

Wilson score interval for a binomial proportion.
Returns (low, high, p_hat). For n==0 returns (nan, nan, nan).

### Function: `analyze_per_episode`

### Function: `plot_fair_eval`

Bar chart: select headline baseline vs oracle binary rates with Wilson error bars.

### Function: `main`

### Function: `pmf`

### Function: `pair`

### Function: `rate`

### Function: `errs`

## ./training/make_plots.py

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

### Function: `rate`

## ./viz/city_map.py

### Class: `RenderConfig`

### Class: `CityMapRenderer`

### Function: `run_live`

### Function: `xy`

### Function: `draw_arrow`

### Function: `render`

### Function: `blit_line`

## ./viz/gradio_demo.py

### Function: `render_map`

### Class: `Session`

### Function: `new_session`

### Function: `step_once`

### Function: `compute_kpis`

### Function: `xy`

## ./viz/record.py

### Function: `record`

Record frames as PNGs.

- `tick_every_frames`: how many frames to show per env.step() (slows animation, looks smoother).  # noqa: E501

### Function: `main`

## ./viz/record_two_phase.py

### Function: `record_phase`

### Function: `main`

