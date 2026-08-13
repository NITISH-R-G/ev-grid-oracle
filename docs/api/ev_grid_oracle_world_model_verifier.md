#### Function: rollout_deterministic_5ticks
Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
This is intentionally verifier-friendly (stable + reproducible) for RLVR.

#### Function: score_prediction
Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
Returns score in [0,1].
