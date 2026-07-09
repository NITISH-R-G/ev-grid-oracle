# Repository Knowledge Graph

## ./test_script.py
- **Classes**: ChargerType, StationState

## ./viz/record_two_phase.py
- **Functions**: _step_action, record_phase, main

## ./viz/record.py
- **Functions**: record, main

## ./viz/gradio_demo.py
- **Classes**: Session
- **Functions**: _norm, _station_color, render_map, new_session, step_once, compute_kpis, xy, _start, _step, _run60, _start_and_maybe_autoplay, _kpis

## ./viz/city_map.py
- **Classes**: RenderConfig, CityMapRenderer
- **Functions**: _station_color, _norm, run_live, __init__, xy, draw_arrow, render, _draw_background, _draw_edges, _draw_glow, _draw_animated_route, blit_line

## ./ev_grid_oracle/road_env.py
- **Classes**: RoadCore
- **Functions**: reset, step, _obs

## ./ev_grid_oracle/road_models.py
- **Classes**: RoadAction, RoadState, RoadObservation
- **Functions**: _non_trivial

## ./ev_grid_oracle/personas.py
- **Classes**: PersonaParams
- **Functions**: choose_persona

## ./ev_grid_oracle/models.py
- **Classes**: ChargerType, ChargeRate, ActionType, DayType, PeakRisk, StationState, EVRequest, BESCOMFeederState, GridState, EVGridAction, EVGridObservation, NegotiationMessage, GridDirective, MultiAgentStepRequest, MultiAgentStepResponse, SimTopStation, SimulationPrediction
- **Functions**: to_jsonable, _occupied_le_total, _check_consistency

## ./ev_grid_oracle/parsing.py
- **Functions**: parse_simulation, parse_action, parse_simulation_and_action

## ./ev_grid_oracle/demand_sim.py
- **Classes**: DemandParams
- **Functions**: _gaussian_bump, expected_arrivals_per_step, sample_arrivals_per_step

## ./ev_grid_oracle/reward_hack.py
- **Classes**: RewardHackDetector
- **Functions**: reset, step, add

## ./ev_grid_oracle/env.py
- **Classes**: EVGridCore
- **Functions**: _peak_risk, _make_ev, _apply_action, _drain_queues_and_charging, _update_station_waits, _build_prompt, reset, step, _apply_tariff_mult

## ./ev_grid_oracle/policies.py
- **Functions**: baseline_policy, always_defer_policy, always_load_shift_policy, nearest_travel_only_policy

## ./ev_grid_oracle/multi_agent.py
- **Classes**: MultiAgentSession
- **Functions**: step, snapshot

## ./ev_grid_oracle/grid_sim.py
- **Classes**: GridParams
- **Functions**: _clamp01, baseline_grid_load, renewable_pct, update_grid_load

## ./ev_grid_oracle/reward.py
- **Classes**: RewardWeights
- **Functions**: _haversine_km, _graph_route_km, compute_reward, split_role_rewards, add_flag, f

## ./ev_grid_oracle/oracle_agent.py
- **Classes**: OracleRuntime, OracleAgent
- **Functions**: load, _ensure_loaded, act, act_with_text, is_active, _generate

## ./ev_grid_oracle/bescom_feed.py
- **Classes**: BESCOMFeedAPI
- **Functions**: snapshot, _stable_seed, _zone_for_station

## ./ev_grid_oracle/scenarios.py
- **Classes**: ScenarioEvent, ScenarioModifiers
- **Functions**: scenario_schedule, apply_scenario_events

## ./ev_grid_oracle/traffic.py
- **Classes**: TrafficModel
- **Functions**: _clamp, _stable_u01, multiplier_for_edge, hotspot

## ./ev_grid_oracle/world_model_verifier.py
- **Classes**: PredictionScore
- **Functions**: _top3, rollout_deterministic_5ticks, score_prediction

## ./ev_grid_oracle/city_graph.py
- **Classes**: StationSpec
- **Functions**: get_station_by_id, get_station_by_slug, haversine_km, _edge_minutes, _add_chain_edges, _add_dense_within_cluster, build_city_graph, travel_time_minutes, nearest_stations_by_geo

## ./server/role_metrics.py
- **Functions**: compute_role_kpis, compute_role_reward_breakdown, _peak_risk_score, summarize_action, part

## ./server/app.py
- **Classes**: DemoNewRequest, MANewRequest, MAAutoStepRequest, DemoSpawnVehicleRequest
- **Functions**: _request_id, _oracle_skip_llm_env, _rate_limit, _demo_oracle_act_with_guard, root, healthz, _osm_route_polyline, _graph_route_polyline, _spawn_road_point_away_from_stations, _demo_session_gc, _demo_session_get, _ma_gc, _ma_get, ma_new, _grid_policy, ma_auto_step, ma_state, ma_step, _obs_to_jsonable, _station_nodes, demo_new, demo_state, demo_spawn_vehicle, demo_step, main, run

## ./server/ev_grid_road_environment.py
- **Classes**: EVGridRoadEnvironment
- **Functions**: __init__, reset, step, state

## ./server/road_router.py
- **Classes**: RoadRouter
- **Functions**: haversine_m, decode_polyline_latlng, get_router, _next, load, nearest_node, route_polyline, _w

## ./server/ev_grid_environment.py
- **Classes**: EVGridEnvironment
- **Functions**: __init__, reset, step, state

## ./.cursor/skills/generate-openenv-env/assets/openenv_env_template/models.py
- **Classes**: __ENV_CLASS_NAME__Action, __ENV_CLASS_NAME__Observation

## ./.cursor/skills/generate-openenv-env/assets/openenv_env_template/client.py
- **Classes**: __ENV_CLASS_NAME__Env
- **Functions**: _step_payload, _parse_result, _parse_state

## ./.cursor/skills/generate-openenv-env/assets/openenv_env_template/server/app.py
- **Functions**: main

## ./.cursor/skills/generate-openenv-env/assets/openenv_env_template/server/__ENV_NAME___environment.py
- **Classes**: __ENV_CLASS_NAME__Environment
- **Functions**: __init__, reset, step, state

## ./tests/test_models_and_graph.py
- **Functions**: test_city_graph_connected_and_25_stations, test_action_route_requires_station_id_and_zero_defer, test_action_defer_requires_positive_defer_minutes, test_time_advances_with_5min_steps

## ./tests/test_policies_collapse.py
- **Functions**: _run_policy, test_collapse_policies_do_not_crash, test_collapse_policies_return_valid_actions_when_pending

## ./tests/test_evaluate_paired.py
- **Functions**: _chdir_repo_root, test_baseline_rollout_identical_for_same_seed_and_scenario, test_oracle_matches_baseline_when_skip_llm, test_evaluate_cli_paired_json, test_fair_eval_cli

## ./tests/test_world_model_verifier.py
- **Functions**: test_rollout_deterministic_is_stable, test_prediction_score_higher_when_close

## ./tests/test_parsing.py
- **Functions**: test_parse_simulation_valid, test_parse_simulation_missing_match, test_parse_simulation_exception_handling

## ./tests/test_reward.py
- **Functions**: test_reward_breakdown_has_keys_and_total, test_deferring_critical_ev_penalized, test_invalid_station_routes_penalized, test_split_role_rewards_exception_handling

## ./tests/test_env_determinism.py
- **Functions**: test_reset_state_identical_two_cores_same_seed, test_step_sequence_identical_two_cores_same_actions, test_ev_grid_action_rejects_malformed_payload, test_route_action_requires_station

## ./tests/test_demo_api.py
- **Functions**: test_demo_new_and_step_roundtrip, test_demo_spawn_vehicle_route_event, test_demo_step_forced_action_validation_422, test_health_shape, test_demo_sessions_ttl_eviction, test_ma_new_and_step_roundtrip

## ./tests/test_fair_eval_mcnemar.py
- **Functions**: test_mcnemar_no_discordant_is_neutral, test_mcnemar_strong_asymmetry_low_p, test_paired_mcnemar_analysis_shape

## ./training/fair_eval.py
- **Functions**: _binom_two_sided_exact_p, mcnemar_discordant, paired_mcnemar_analysis, wilson_interval, _binary_keys, analyze_per_episode, _paired_improvement_counts, plot_fair_eval, main, pmf, pair, rate, errs

## ./training/make_plots.py
- **Functions**: _boxplot_compat, _per_episode_rows, plot_kpi_bars, plot_episode_trajectories, plot_delta_histograms, plot_reward_breakdown, plot_boxplots, plot_oracle_win_rates, plot_paired_scatter, plot_binary_timeline, plot_fair_eval_rates, plot_mcnemar_summary, plot_dashboard_grid, main, rate

## ./training/evaluate.py
- **Classes**: EpisodeMetrics
- **Functions**: _episode_metrics_to_json, run_episode, summarize, summarize_reward_breakdown, main

## ./tools/docs_sync.py
- **Functions**: extract_api_info, update_readme

## ./tools/fetch_bangalore_roads_overpass.py
- **Functions**: _chunk, _overpass_query, _tile_bbox, _http_post, _to_geojson, main

## ./tools/export_grpo_tensorboard_plots.py
- **Functions**: _pick_tags, main, plot_tag

## ./tools/build_roads_render.py
- **Functions**: main

## ./tools/sync_space_to_hub.py
- **Functions**: main

## ./tools/write_eval_snapshot.py
- **Functions**: main

## ./tools/generate_knowledge_graph.py
- **Functions**: generate_knowledge_graph

## ./tools/generate_health_dashboard.py
- **Functions**: run_cmd, get_git_stats, get_leaderboard, get_documentation_health, fetch_github_stats, run_pytest_cov, run_radon, run_bandit, run_ruff, calculate_health_scores, generate_ai_insights, main

## ./tools/build_road_graph.py
- **Classes**: Node
- **Functions**: haversine_m, _encode_signed, encode_polyline_latlng, speed_kmh, snap, _coords_latlng_from_geojson_line, parse_args, build_adjacency, contract_edges, filter_largest_component, main, add_neighbor, get_node, flush

## ./tools/road_reward_smoke.py
- **Functions**: main, parse, reward

## ./tools/fetch_osm_roads.py
- **Classes**: BBox
- **Functions**: _fetch_overpass, _simplify_line, _to_feature_collection, build_query, main

## ./tools/prune_osm_geojson.py
- **Functions**: _pad_bbox, _line_intersects_bbox, _simplify_uniform, main

