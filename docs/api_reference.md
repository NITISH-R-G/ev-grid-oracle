# API Documentation

Automatically generated from source code.

## server/role_metrics.py

#### Function: compute_role_reward_breakdown
Lightweight, explainable credit assignment for demo storytelling.

This is NOT a full MARL credit assignment — it allocates the *same* component
values across roles with fixed weights so totals remain easy to interpret.

## server/__init__.py

### Module: __init__.py
Server package for OpenEnv runtime.

## server/app.py

#### Function: _demo_oracle_act_with_guard
Run oracle policy with CPU-Space-safe guards.

Returns: action, oracle_text, oracle_llm_active, oracle_timed_out, oracle_skipped_env

#### Function: healthz
HF Spaces / cold-start friendly health endpoint.
Keep it fast and dependency-safe (no heavy routing work).

#### Function: _graph_route_polyline
Return a render-friendly polyline (lat/lng pairs) along the station graph.
v0 fallback was a straight line; this produces a multi-point path so the UI reads like navigation.

#### Function: _spawn_road_point_away_from_stations
Pick a deterministic road-graph node location (lat,lng) that is not within
`min_station_dist_m` of any station. Deterministic for a given seed_key.

#### Function: demo_spawn_vehicle
Spawn a new EV at a valid road location (away from stations) and immediately compute
an assignment + route event for the frontend.

## server/ev_grid_road_environment.py

#### Class: EVGridRoadEnvironment
Separate OpenEnv environment that forces real-road-graph actions.
Mounted as a sub-app under /road/ so it doesn't break the existing env.

## ev_grid_oracle/__init__.py

### Module: __init__.py
EV Grid Oracle package.

## ev_grid_oracle/road_models.py

#### Class: RoadAction
Minimal action space for RL on a real road graph:
choose the next connected node (no teleportation).

## ev_grid_oracle/models.py

#### Class: BESCOMFeederState
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

#### Class: NegotiationMessage
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

#### Class: GridDirective
GridOperator -> FleetDispatcher constraint signal (verifiable).

#### Class: SimulationPrediction
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## ev_grid_oracle/parsing.py

#### Function: parse_simulation_and_action
Parse both dream prediction and action (either can be missing).

## ev_grid_oracle/reward_hack.py

#### Class: RewardHackDetector
Stateful, deterministic detector for common reward-hacking patterns.

Goal: give the existing anti-hack flags "teeth" by detecting multi-step
exploit patterns, not just single-step invalidity.

## ev_grid_oracle/env.py

#### Class: EVGridCore
Core env logic (no HTTP). Server wraps this.

v0 slice: deterministic schema, minimal dynamics.
Next slices add demand_sim/grid_sim/reward engine.

## ev_grid_oracle/policies.py

#### Function: baseline_policy
Greedy baseline: pick station minimizing (travel_time + wait + stress + price), avoid full.

Deterministic given state.

#### Function: always_defer_policy
Collapse baseline: always defer (reward-hack / fairness stressor).

#### Function: always_load_shift_policy
Collapse baseline: always load_shift on head EV (ignores queues / grid).

#### Function: nearest_travel_only_policy
Collapse baseline: minimize travel time only (ignores price, wait, stress).
Used to show greedy multi-objective baseline is not trivially dominated.

## ev_grid_oracle/multi_agent.py

#### Class: MultiAgentSession
Minimal explicit multi-agent wrapper around EVGridCore.

- GridOperator emits a directive (constraint signal) + optional message.
- FleetDispatcher emits an action + optional message.
- Resolver applies directive deterministically and steps EVGridCore.

##### Method: MultiAgentSession.snapshot
Read-only view of the underlying core state.

## ev_grid_oracle/reward.py

#### Function: _graph_route_km
Approximate driving distance along the city graph using haversine edge weights.
Returns None if no path exists.

#### Function: compute_reward
Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.

#### Function: split_role_rewards
Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.

## ev_grid_oracle/oracle_agent.py

#### Class: OracleRuntime
Singleton-style loader that prefers CUDA when available.

This keeps T4 Spaces fast and makes oracle behavior undeniable.

#### Class: OracleAgent
Oracle agent wrapper.

Default: baseline fallback (always available).
Optional: load a trained LoRA adapter when `lora_repo_id` provided.

## ev_grid_oracle/bescom_feed.py

#### Class: BESCOMFeedAPI
Deterministic BESCOM feeder "API mock".

- No network calls (HF Spaces safe).
- Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
- Output is stable under (seed, scenario, tick) so judge replays match.

## ev_grid_oracle/scenarios.py

#### Class: ScenarioModifiers
Lightweight knobs applied on top of the core simulator.
These are intentionally simple and deterministic for replayable judging.

#### Function: scenario_schedule
Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

Note: ticks are env steps (5-minute increments by default).

#### Function: apply_scenario_events
Returns updated modifiers and the list of events that fired this tick.

## ev_grid_oracle/traffic.py

#### Function: _stable_u01
Stable pseudo-random in [0,1) from input parts.
Deterministic across processes and Python versions.

#### Class: TrafficModel
Deterministic synthetic traffic for hackathon demos.

Returns a multiplier m in [0.35, 1.15] to scale base travel_s on an edge.

## ev_grid_oracle/world_model_verifier.py

#### Function: rollout_deterministic_5ticks
Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
This is intentionally verifier-friendly (stable + reproducible) for RLVR.

#### Function: score_prediction
Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].
