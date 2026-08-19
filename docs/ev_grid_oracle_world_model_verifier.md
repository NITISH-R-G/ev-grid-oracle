# Documentation for ev_grid_oracle/world_model_verifier.py

## Classes

### PredictionScore
## Functions

### _top3
### rollout_deterministic_5ticks
```text
Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
This is intentionally verifier-friendly (stable + reproducible) for RLVR.
```

### score_prediction
```text
Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].
```
