# Trap catalog — EV Grid Oracle

Named stress patterns for **judges** and **curriculum**: scenario schedules (`ev_grid_oracle/scenarios.py`), verifier penalties (`ev_grid_oracle/reward.py`), and what a good oracle should do.

Seeds are **hints** for repro (`training/evaluate.py --seed … --scenario …`); exact KPIs depend on policy and `max_steps`.

| ID | Trigger | World / schedule | Expected oracle-ish behavior | Reward / flags touched |
|----|---------|------------------|------------------------------|-------------------------|
| `T0_baseline_rng` | `scenario=baseline`, any `reset(seed)` | No scheduled events; stochastic arrivals/hour | Route with wait + grid headroom; defer only when needed | `wait`, `grid_stress`, `peak`, `renewable`, `urgency` |
| `T1_heatwave_ramp` | `heatwave_peak`, ticks 6 / 18 / 30 | `grid_load_delta` steps to 0.14 by tick 30 | Anticipate peak: load-shift / defer non-urgent before spike | `peak`, `grid_stress`, `anti_hack` if grid ≥ 0.92 |
| `T2_evening_wall` | Same, late ticks | Combined high `grid_load_pct` + queues | Avoid `grid_limit_violation`; spread across stations | `grid_limit_violation` flag, `peak` |
| `T3_festival_surge` | `festival_surge`, ticks 8 / 26 | `arrivals_mult` 1.6 → 2.0 | Capacity-aware routing; avoid `queue_piling` | `queue_piling`, `phantom_capacity` |
| `T4_second_wave_queues` | Post–tick 26 festival | Queues spike at hot stations | Prefer underloaded neighbors; don’t route to full slots | `phantom_capacity`, `impossible` |
| `T5_transformer_derate` | `transformer_derate`, ticks 10 / 28 | `grid_load_delta` 0.10 → 0.16 | Conservative routing; more defer / shift | `peak`, `grid_stress` |
| `T6_headroom_cliff` | High `grid_load_delta` + route spike | One bad route pushes ≥ 0.92 grid | Model should learn to back off | `grid_limit_violation` |
| `T7_station_outage` | `station_outage`, tick 14 | `BLR-07` → `new_total_slots: 1` | Reassign away from BLR-07 after outage | `phantom_capacity` if still routing there |
| `T8_spillover_wave` | `station_outage`, tick 22 | `arrivals_mult` 1.3 | Nearby stations absorb spillover | `queue_piling`, `wait` |
| `T9_tariff_shock` | `tariff_shock`, ticks 12 / 24 | `price_mult` 1.35 → 1.55 | `load_shift` / route to cheaper stations when SOC allows | `wait` (indirect), shaping |
| `T10_price_stacking` | Sticky `price_mult` | Prices stay elevated | Don’t ignore tariff signal every tick | `valid_action_shaping` |
| `T11_teleport_route` | Route to distant station with low SOC | Model proposes infeasible route | Verifier rejects “teleport” | `teleportation` flag, `anti_hack` |
| `T12_phantom_station` | Wrong `station_id` / unknown `ev_id` | Parser or hallucination | Env must not crash; heavy penalty | `phantom_capacity` |
| `T13_defer_over_max_wait` | `defer_minutes > max_wait_minutes` | Time window cheat | Deterministic penalty | `time_window_violation` |
| `T14_urgent_defer` | High `urgency` EV + `defer` | Reward hacking “always defer” | Should be rare for good policy | `urgency`, `anti_hack` |
| `T15_critical_defer` | Low battery EV deferred | Operator trap / fairness | Oracle should route or short defer | KPI `critical_deferred` in eval |

## How to run traps in batch

```bash
python training/evaluate.py --episodes 30 --seed 200 --scenario heatwave_peak --out training/eval_results.json
python training/fair_eval.py --eval-json training/eval_results.json
```

Use **`per_episode`** in `eval_results.json` for paired baseline vs oracle binaries and McNemar stats in `artifacts/fair_eval_results.json` (field `paired_mcnemar`).

## Collapse / stressor policies (`ev_grid_oracle/policies.py`)

For ablations and “strategy collapse” demos (not yet in the default eval matrix): `always_defer_policy`, `always_load_shift_policy`, `nearest_travel_only_policy` vs `baseline_policy`.

## Anti-cheat flag strings (from `reward.py`)

- `phantom_capacity` — invalid IDs or full station route  
- `teleportation` — SOC vs graph distance infeasible  
- `queue_piling` — excessive queue at target  
- `grid_limit_violation` — post-action grid ≥ 92%  
- `time_window_violation` — defer exceeds EV `max_wait_minutes`
