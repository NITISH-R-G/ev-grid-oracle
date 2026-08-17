# Documentation for ./ev_grid_oracle/models.py

### BESCOMFeederState

Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### NegotiationMessage

A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### GridDirective

GridOperator -> FleetDispatcher constraint signal (verifiable).

### SimulationPrediction

Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.
