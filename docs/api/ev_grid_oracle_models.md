# API Reference: `ev_grid_oracle/models.py`

## Classes

### `ChargerType`
No documentation available.

### `ChargeRate`
No documentation available.

### `ActionType`
No documentation available.

### `DayType`
No documentation available.

### `PeakRisk`
No documentation available.

### `StationState`
No documentation available.

### `EVRequest`
No documentation available.

### `BESCOMFeederState`
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### `GridState`
No documentation available.

### `EVGridAction`
No documentation available.

### `EVGridObservation`
No documentation available.

### `NegotiationMessage`
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### `GridDirective`
GridOperator -> FleetDispatcher constraint signal (verifiable).

### `MultiAgentStepRequest`
No documentation available.

### `MultiAgentStepResponse`
No documentation available.

### `SimTopStation`
No documentation available.

### `SimulationPrediction`
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Functions

### `to_jsonable`
No documentation available.

### `_occupied_le_total`
No documentation available.

### `_check_consistency`
No documentation available.
