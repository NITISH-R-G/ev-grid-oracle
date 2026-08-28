# Documentation for ev_grid_oracle/models.py

## Classes

### ChargerType
No docstring provided.

### ChargeRate
No docstring provided.

### ActionType
No docstring provided.

### DayType
No docstring provided.

### PeakRisk
No docstring provided.

### StationState
No docstring provided.

### EVRequest
No docstring provided.

### BESCOMFeederState
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

### GridState
No docstring provided.

### EVGridAction
No docstring provided.

### EVGridObservation
No docstring provided.

### NegotiationMessage
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

### GridDirective
GridOperator -> FleetDispatcher constraint signal (verifiable).

### MultiAgentStepRequest
No docstring provided.

### MultiAgentStepResponse
No docstring provided.

### SimTopStation
No docstring provided.

### SimulationPrediction
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Functions

### to_jsonable
No docstring provided.

### _occupied_le_total
No docstring provided.

### _check_consistency
No docstring provided.
