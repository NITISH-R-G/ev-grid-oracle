# Documentation for `./ev_grid_oracle/models.py`

## Classes

### `ChargerType`
*No docstring available.*

### `ChargeRate`
*No docstring available.*

### `ActionType`
*No docstring available.*

### `DayType`
*No docstring available.*

### `PeakRisk`
*No docstring available.*

### `StationState`
*No docstring available.*

### `EVRequest`
*No docstring available.*

### `BESCOMFeederState`
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### `GridState`
*No docstring available.*

### `EVGridAction`
*No docstring available.*

### `EVGridObservation`
*No docstring available.*

### `NegotiationMessage`
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### `GridDirective`
GridOperator -> FleetDispatcher constraint signal (verifiable).

### `MultiAgentStepRequest`
*No docstring available.*

### `MultiAgentStepResponse`
*No docstring available.*

### `SimTopStation`
*No docstring available.*

### `SimulationPrediction`
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Functions

### `to_jsonable`
*No docstring available.*

### `_occupied_le_total`
*No docstring available.*

### `_check_consistency`
*No docstring available.*
