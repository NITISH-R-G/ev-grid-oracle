# Documentation for `./ev_grid_oracle/traffic.py`

## Classes

### TrafficModel
Deterministic synthetic traffic for hackathon demos.

Returns a multiplier m in [0.35, 1.15] to scale base travel_s on an edge.

**Methods:**
- `multiplier_for_edge`

## Functions

### _clamp

### _stable_u01
Stable pseudo-random in [0,1) from input parts.
Deterministic across processes and Python versions.
