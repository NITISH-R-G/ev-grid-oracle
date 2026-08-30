# Documentation for `ev_grid_oracle/world_model_verifier.py`

## Classes

### Class `PredictionScore`

No documentation provided.

## Functions

### Function `_top3`

No documentation provided.

### Function `rollout_deterministic_5ticks`

Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
This is intentionally verifier-friendly (stable + reproducible) for RLVR.

### Function `score_prediction`

Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].
