# Documentation for `ev_grid_oracle/models.py`

## Classes

### Class `ChargerType`

No documentation provided.

### Class `ChargeRate`

No documentation provided.

### Class `ActionType`

No documentation provided.

### Class `DayType`

No documentation provided.

### Class `PeakRisk`

No documentation provided.

### Class `StationState`

No documentation provided.

### Class `EVRequest`

No documentation provided.

### Class `BESCOMFeederState`

Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### Class `GridState`

No documentation provided.

### Class `EVGridAction`

No documentation provided.

### Class `EVGridObservation`

No documentation provided.

### Class `NegotiationMessage`

A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### Class `GridDirective`

GridOperator -> FleetDispatcher constraint signal (verifiable).

### Class `MultiAgentStepRequest`

No documentation provided.

### Class `MultiAgentStepResponse`

No documentation provided.

### Class `SimTopStation`

No documentation provided.

### Class `SimulationPrediction`

Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Functions

### Function `to_jsonable`

No documentation provided.

### Function `_occupied_le_total`

No documentation provided.

### Function `_check_consistency`

No documentation provided.
