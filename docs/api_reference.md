# API Reference

This document is automatically generated from the docstrings in the source code.

## `ev_grid_oracle/__init__.py`

**Module Docstring:**

```text
EV Grid Oracle package.
```

---

## `ev_grid_oracle/bescom_feed.py`

### Classes

#### `BESCOMFeedAPI`

```text
Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.
```


---

## `ev_grid_oracle/city_graph.py`

### Classes

#### `StationSpec`

### Functions

#### `get_station_by_id()`

#### `get_station_by_slug()`

#### `haversine_km()`

#### `_edge_minutes()`

#### `_add_chain_edges()`

#### `_add_dense_within_cluster()`

#### `build_city_graph()`

#### `travel_time_minutes()`

#### `nearest_stations_by_geo()`

---

## `ev_grid_oracle/demand_sim.py`

### Classes

#### `DemandParams`

### Functions

#### `_gaussian_bump()`

#### `expected_arrivals_per_step()`

#### `sample_arrivals_per_step()`

---

## `ev_grid_oracle/env.py`

### Classes

#### `EVGridCore`

```text
Core env logic (no HTTP). Server wraps this.

v0 slice: deterministic schema, minimal dynamics.
Next slices add demand_sim/grid_sim/reward engine.
```


### Functions

#### `_peak_risk()`

#### `_make_ev()`

#### `_apply_action()`

#### `_drain_queues_and_charging()`

#### `_update_station_waits()`

#### `_build_prompt()`

---

## `ev_grid_oracle/grid_sim.py`

### Classes

#### `GridParams`

### Functions

#### `_clamp01()`

#### `baseline_grid_load()`

#### `renewable_pct()`

#### `update_grid_load()`

---

## `ev_grid_oracle/models.py`

### Classes

#### `ChargerType`

#### `ChargeRate`

#### `ActionType`

#### `DayType`

#### `PeakRisk`

#### `StationState`


#### `EVRequest`

#### `BESCOMFeederState`

```text
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).
```

#### `GridState`

#### `EVGridAction`


#### `EVGridObservation`

#### `NegotiationMessage`

```text
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.
```

#### `GridDirective`

```text
GridOperator -> FleetDispatcher constraint signal (verifiable).
```

#### `MultiAgentStepRequest`

#### `MultiAgentStepResponse`

#### `SimTopStation`

#### `SimulationPrediction`

```text
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.
```

### Functions

#### `to_jsonable()`

---

## `ev_grid_oracle/multi_agent.py`

### Classes

#### `MultiAgentSession`

```text
Minimal explicit multi-agent wrapper around EVGridCore.

- GridOperator emits a directive (constraint signal) + optional message.
- FleetDispatcher emits an action + optional message.
- Resolver applies directive deterministically and steps EVGridCore.
```

- **`snapshot()`**: Read-only view of the underlying core state.

---

## `ev_grid_oracle/oracle_agent.py`

### Classes

#### `OracleRuntime`

```text
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.
```


#### `OracleAgent`

```text
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.
```


---

## `ev_grid_oracle/parsing.py`

### Functions

#### `parse_simulation()`

#### `parse_action()`

#### `parse_simulation_and_action()`

```text
Parse both dream prediction and action (either can be missing).
```

---

## `ev_grid_oracle/personas.py`

### Classes

#### `PersonaParams`

### Functions

#### `choose_persona()`

---

## `ev_grid_oracle/policies.py`

### Functions

#### `baseline_policy()`

```text
Greedy baseline: pick station minimizing (travel_time + wait + stress + price), avoid full.

Deterministic given state.
```

#### `always_defer_policy()`

```text
Collapse baseline: always defer (reward-hack / fairness stressor).
```

#### `always_load_shift_policy()`

```text
Collapse baseline: always load_shift on head EV (ignores queues / grid).
```

#### `nearest_travel_only_policy()`

```text
Collapse baseline: minimize travel time only (ignores price, wait, stress).
Used to show greedy multi-objective baseline is not trivially dominated.
```

---

## `ev_grid_oracle/reward.py`

### Classes

#### `RewardWeights`

### Functions

#### `_haversine_km()`

#### `_graph_route_km()`

```text
Approximate driving distance along the city graph using haversine edge weights.
Returns None if no path exists.
```

#### `compute_reward()`

```text
Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.
```

#### `split_role_rewards()`

```text
Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.
```

---

## `ev_grid_oracle/reward_hack.py`

### Classes

#### `RewardHackDetector`

```text
Stateful, deterministic detector for common reward-hacking patterns.

Goal: give the existing anti-hack flags "teeth" by detecting multi-step
exploit patterns, not just single-step invalidity.
```


---

## `ev_grid_oracle/road_env.py`

### Classes

#### `RoadCore`


---

## `ev_grid_oracle/road_models.py`

### Classes

#### `RoadAction`

```text
Minimal action space for RL on a real road graph:
choose the next connected node (no teleportation).
```


#### `RoadState`

#### `RoadObservation`

---

## `ev_grid_oracle/scenarios.py`

### Classes

#### `ScenarioEvent`

#### `ScenarioModifiers`

```text
Lightweight knobs applied on top of the core simulator.
These are intentionally simple and deterministic for replayable judging.
```

### Functions

#### `scenario_schedule()`

```text
Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

Note: ticks are env steps (5-minute increments by default).
```

#### `apply_scenario_events()`

```text
Returns updated modifiers and the list of events that fired this tick.
```

---

## `ev_grid_oracle/traffic.py`

### Classes

#### `TrafficModel`

```text
Deterministic synthetic traffic for hackathon demos.

Returns a multiplier m in [0.35, 1.15] to scale base travel_s on an edge.
```


### Functions

#### `_clamp()`

#### `_stable_u01()`

```text
Stable pseudo-random in [0,1) from input parts.
Deterministic across processes and Python versions.
```

---

## `ev_grid_oracle/world_model_verifier.py`

### Classes

#### `PredictionScore`

### Functions

#### `_top3()`

#### `rollout_deterministic_5ticks()`

```text
Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
This is intentionally verifier-friendly (stable + reproducible) for RLVR.
```

#### `score_prediction()`

```text
Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].
```

---

## `server/__init__.py`

**Module Docstring:**

```text
Server package for OpenEnv runtime.
```

---

## `server/app.py`

### Classes

#### `DemoNewRequest`

#### `MANewRequest`

#### `MAAutoStepRequest`

#### `DemoSpawnVehicleRequest`

### Functions

#### `_request_id()`

#### `_oracle_skip_llm_env()`

#### `_rate_limit()`

#### `_demo_oracle_act_with_guard()`

```text
Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env
```

#### `root()`

#### `healthz()`

```text
HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).
```

#### `_osm_route_polyline()`

#### `_graph_route_polyline()`

```text
Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.
```

#### `_spawn_road_point_away_from_stations()`

```text
Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.
```

#### `_demo_session_gc()`

#### `_demo_session_get()`

#### `_ma_gc()`

#### `_ma_get()`

#### `ma_new()`

#### `_grid_policy()`

#### `ma_auto_step()`

#### `ma_state()`

#### `ma_step()`

#### `_obs_to_jsonable()`

#### `_station_nodes()`

#### `demo_new()`

#### `demo_state()`

#### `demo_spawn_vehicle()`

```text
Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.
```

#### `demo_step()`

#### `main()`

---

## `server/ev_grid_environment.py`

### Classes

#### `EVGridEnvironment`


---

## `server/ev_grid_road_environment.py`

### Classes

#### `EVGridRoadEnvironment`

```text
Separate OpenEnv environment that forces real-road-graph actions.
Mounted as a sub-app under /road/ so it doesn't break the existing env.
```


---

## `server/road_router.py`

### Classes

#### `RoadRouter`


### Functions

#### `haversine_m()`

#### `decode_polyline_latlng()`

#### `get_router()`

---

## `server/role_metrics.py`

### Functions

#### `compute_role_kpis()`

#### `compute_role_reward_breakdown()`

```text
Lightweight, explainable credit assignment for demo storytelling.

This is NOT a full MARL credit assignment — it allocates the *same* component
values across roles with fixed weights so totals remain easy to interpret.
```

#### `_peak_risk_score()`

#### `summarize_action()`

---

## `test_script.py`

### Classes

#### `ChargerType`

#### `StationState`

---

## `tests/test_demo_api.py`

### Functions

#### `test_demo_new_and_step_roundtrip()`

#### `test_demo_spawn_vehicle_route_event()`

#### `test_demo_step_forced_action_validation_422()`

#### `test_health_shape()`

#### `test_demo_sessions_ttl_eviction()`

#### `test_ma_new_and_step_roundtrip()`

---

## `tests/test_env_determinism.py`

**Module Docstring:**

```text
Determinism + strict action validation (core env, no LLM).
```

### Functions

#### `test_reset_state_identical_two_cores_same_seed()`

#### `test_step_sequence_identical_two_cores_same_actions()`

#### `test_ev_grid_action_rejects_malformed_payload()`

#### `test_route_action_requires_station()`

---

## `tests/test_evaluate_paired.py`

### Functions

#### `_chdir_repo_root()`

#### `test_baseline_rollout_identical_for_same_seed_and_scenario()`

#### `test_oracle_matches_baseline_when_skip_llm()`

#### `test_evaluate_cli_paired_json()`

#### `test_fair_eval_cli()`

---

## `tests/test_fair_eval_mcnemar.py`

### Functions

#### `test_mcnemar_no_discordant_is_neutral()`

#### `test_mcnemar_strong_asymmetry_low_p()`

#### `test_paired_mcnemar_analysis_shape()`

---

## `tests/test_models_and_graph.py`

### Functions

#### `test_city_graph_connected_and_25_stations()`

#### `test_action_route_requires_station_id_and_zero_defer()`

#### `test_action_defer_requires_positive_defer_minutes()`

#### `test_time_advances_with_5min_steps()`

---

## `tests/test_parsing.py`

### Functions

#### `test_parse_simulation_valid()`

#### `test_parse_simulation_missing_match()`

#### `test_parse_simulation_exception_handling()`

---

## `tests/test_policies_collapse.py`

**Module Docstring:**

```text
Smoke tests for collapse / stressor policies (deterministic, no env crashes).
```

### Functions

#### `_run_policy()`

#### `test_collapse_policies_do_not_crash()`

#### `test_collapse_policies_return_valid_actions_when_pending()`

---

## `tests/test_reward.py`

### Functions

#### `test_reward_breakdown_has_keys_and_total()`

#### `test_deferring_critical_ev_penalized()`

#### `test_invalid_station_routes_penalized()`

#### `test_split_role_rewards_exception_handling()`

---

## `tests/test_world_model_verifier.py`

### Functions

#### `test_rollout_deterministic_is_stable()`

#### `test_prediction_score_higher_when_close()`

---

## `tools/build_road_graph.py`

### Classes

#### `Node`

### Functions

#### `haversine_m()`

#### `_encode_signed()`

#### `encode_polyline_latlng()`

```text
Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.
```

#### `speed_kmh()`

#### `snap()`

#### `_coords_latlng_from_geojson_line()`

#### `parse_args()`

#### `build_adjacency()`

```text
Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.
```

#### `contract_edges()`

```text
Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.
```

#### `filter_largest_component()`

```text
Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.
```

#### `main()`

---

## `tools/build_roads_render.py`

### Functions

#### `main()`

---

## `tools/docs_sync.py`

### Functions

#### `extract_docstrings_from_file()`

```text
Parses a Python file and extracts docstrings for functions and classes.
```

#### `collect_all_docstrings()`

```text
Walks the repository and collects all docstrings.
```

#### `write_api_reference()`

```text
Writes the collected docstrings to a Markdown file.
```

---

## `tools/export_grpo_tensorboard_plots.py`

**Module Docstring:**

```text
Export loss + reward (or closest TRL scalar tags) from a TensorBoard run dir into PNGs.

Hackathon requirement: committed plots from a *real* GRPO run. After `trainer.train()` in
`training/train_grpo.ipynb`, copy `ev_oracle_grpo_road/` from Colab (or run locally), then:

  pip install tensorboard matplotlib
  python tools/export_grpo_tensorboard_plots.py --logdir ev_oracle_grpo_road --out-dir artifacts

Writes e.g. artifacts/grpo_loss.png and artifacts/grpo_reward.png (filenames depend on tags found).
```

### Functions

#### `_pick_tags()`

#### `main()`

---

## `tools/fetch_bangalore_roads_overpass.py`

### Functions

#### `_chunk()`

#### `_overpass_query()`

#### `_tile_bbox()`

#### `_http_post()`

#### `_to_geojson()`

#### `main()`

---

## `tools/fetch_osm_roads.py`

### Classes

#### `BBox`

### Functions

#### `_fetch_overpass()`

#### `_simplify_line()`

#### `_to_feature_collection()`

#### `build_query()`

#### `main()`

---

## `tools/generate_health_dashboard.py`

### Functions

#### `run_cmd()`

#### `get_git_stats()`

#### `get_leaderboard()`

#### `get_documentation_health()`

#### `fetch_github_stats()`

#### `run_pytest_cov()`

#### `run_radon()`

#### `run_bandit()`

#### `run_ruff()`

#### `calculate_health_scores()`

#### `generate_ai_insights()`

#### `main()`

---

## `tools/generate_knowledge_graph.py`

### Functions

#### `extract_info_from_file()`

```text
Parses a Python file and extracts functions, classes, and their docstrings.
```

#### `generate_knowledge_graph()`

```text
Generates a knowledge graph of the repository.
```

#### `save_knowledge_graph()`

```text
Saves the knowledge graph to JSON and Markdown formats.
```

---

## `tools/prune_osm_geojson.py`

### Functions

#### `_pad_bbox()`

#### `_line_intersects_bbox()`

#### `_simplify_uniform()`

#### `main()`

---

## `tools/road_reward_smoke.py`

### Functions

#### `main()`

---

## `tools/sync_space_to_hub.py`

**Module Docstring:**

```text
Push this repo to a Hugging Face *Space* without using `git push` (avoids Hub binary rejections).

Docker Spaces often have **no** “link GitHub repo” in Settings — the Space is its own Hub git repo.
Use this script after `git push origin main`; it uploads sources + a fresh `web/dist` via the Hub API.

Usage:
  cd repo root
  npm --prefix web run build    # or let this script run it (default)
  python tools/sync_space_to_hub.py

Requires: `pip install huggingface_hub`, token with write access (`HF_TOKEN` or `huggingface-cli login`).
```

### Functions

#### `main()`

---

## `tools/write_eval_snapshot.py`

**Module Docstring:**

```text
Run a tiny paired evaluate.py job and write artifacts/eval_snapshot.json (no LLM).
```

### Functions

#### `main()`

---

## `training/__init__.py`

**Module Docstring:**

```text
Training scripts (not imported by server/runtime).
```

---

## `training/evaluate.py`

### Classes

#### `EpisodeMetrics`

### Functions

#### `_episode_metrics_to_json()`

#### `run_episode()`

#### `summarize()`

#### `summarize_reward_breakdown()`

#### `main()`

---

## `training/fair_eval.py`

### Functions

#### `_binom_two_sided_exact_p()`

```text
Two-sided exact test for Binomial(n, p); used for McNemar discordant pairs (p=0.5).
```

#### `mcnemar_discordant()`

```text
McNemar on paired binary outcomes.
b01 = count(baseline True, oracle False); b10 = count(baseline False, oracle True).
```

#### `paired_mcnemar_analysis()`

```text
Paired McNemar for headline binaries (same rows as Wilson chart).
```

#### `wilson_interval()`

```text
Wilson score interval for a binomial proportion.
Returns (low, high, p_hat). For n==0 returns (nan, nan, nan).
```

#### `_binary_keys()`

#### `analyze_per_episode()`

#### `_paired_improvement_counts()`

```text
Operational 'wins' where oracle strictly improves a binary bad outcome vs baseline.
```

#### `plot_fair_eval()`

```text
Bar chart: select headline baseline vs oracle binary rates with Wilson error bars.
```

#### `main()`

---

## `training/make_plots.py`

### Functions

#### `_boxplot_compat()`

#### `_per_episode_rows()`

#### `plot_kpi_bars()`

#### `plot_episode_trajectories()`

#### `plot_delta_histograms()`

#### `plot_reward_breakdown()`

#### `plot_boxplots()`

#### `plot_oracle_win_rates()`

#### `plot_paired_scatter()`

#### `plot_binary_timeline()`

#### `plot_fair_eval_rates()`

#### `plot_mcnemar_summary()`

#### `plot_dashboard_grid()`

#### `main()`

---

## `viz/city_map.py`

### Classes

#### `RenderConfig`

#### `CityMapRenderer`


### Functions

#### `_station_color()`

#### `_norm()`

#### `run_live()`

---

## `viz/gradio_demo.py`

### Classes

#### `Session`

### Functions

#### `_norm()`

#### `_station_color()`

#### `render_map()`

#### `new_session()`

#### `step_once()`

#### `compute_kpis()`

---

## `viz/record.py`

### Functions

#### `record()`

```text
Record frames as PNGs.

- `tick_every_frames`: how many frames to show per env.step() (slows animation, looks smoother).
```

#### `main()`

---

## `viz/record_two_phase.py`

### Functions

#### `_step_action()`

#### `record_phase()`

#### `main()`

---
