# Documentation for `./ev_grid_oracle/models.py`

## Classes

### ChargerType

### ChargeRate

### ActionType

### DayType

### PeakRisk

### StationState

**Methods:**
- `_occupied_le_total`

### EVRequest

### BESCOMFeederState
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### GridState

### EVGridAction

**Methods:**
- `_check_consistency`

### EVGridObservation

### NegotiationMessage
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### GridDirective
GridOperator -> FleetDispatcher constraint signal (verifiable).

### MultiAgentStepRequest

### MultiAgentStepResponse

### SimTopStation

### SimulationPrediction
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Functions

### to_jsonable
