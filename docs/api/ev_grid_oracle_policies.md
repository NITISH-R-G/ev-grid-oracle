# Documentation for ev_grid_oracle/policies.py

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
