### Function: _graph_route_km

Approximate driving distance along the city graph using haversine edge weights.
Returns None if no path exists.

### Function: compute_reward

Deterministic, verifier-style reward with breakdown.

Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.

### Function: split_role_rewards

Deterministic role-level reward views derived from the same underlying breakdown.

This is intentionally simple and bounded (judge-friendly): it does not claim
full MARL credit assignment, but it does make incentives explicit.
