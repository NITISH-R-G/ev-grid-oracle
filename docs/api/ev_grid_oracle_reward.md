# Documentation for `./ev_grid_oracle/reward.py`

## Classes

### `RewardWeights`
*No docstring available.*

## Functions

### `_haversine_km`
*No docstring available.*

### `_graph_route_km`
Approximate driving distance along the city graph using haversine edge weights.
Returns None if no path exists.

### `compute_reward`
Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.

### `split_role_rewards`
Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.

### `add_flag`
*No docstring available.*

### `f`
*No docstring available.*
