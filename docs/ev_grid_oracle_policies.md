# Documentation for ev_grid_oracle/policies.py

## Functions

### baseline_policy
```text
Greedy baseline: pick station minimizing (travel_time + wait + stress + price), avoid full.

Deterministic given state.
```

### always_defer_policy
```text
Collapse baseline: always defer (reward-hack / fairness stressor).
```

### always_load_shift_policy
```text
Collapse baseline: always load_shift on head EV (ignores queues / grid).
```

### nearest_travel_only_policy
```text
Collapse baseline: minimize travel time only (ignores price, wait, stress).
Used to show greedy multi-objective baseline is not trivially dominated.
```
