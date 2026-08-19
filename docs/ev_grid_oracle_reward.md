# Documentation for ev_grid_oracle/reward.py

## Classes

### RewardWeights
## Functions

### _haversine_km
### _graph_route_km
```text
Approximate driving distance along the city graph using haversine edge weights.
Returns None if no path exists.
```

### compute_reward
```text
Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.
```

### split_role_rewards
```text
Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.
```

### add_flag
### f
