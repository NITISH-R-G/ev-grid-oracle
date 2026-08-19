# Documentation for ev_grid_oracle/env.py

## Classes

### EVGridCore
```text
Core env logic (no HTTP). Server wraps this.

v0 slice: deterministic schema, minimal dynamics.
Next slices add demand_sim/grid_sim/reward engine.
```

## Functions

### _peak_risk
### _make_ev
### _apply_action
### _drain_queues_and_charging
### _update_station_waits
### _build_prompt
### reset
### step
### _apply_tariff_mult
