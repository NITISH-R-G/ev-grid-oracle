# Documentation for ev_grid_oracle/models.py

## Classes

### ChargerType
### ChargeRate
### ActionType
### DayType
### PeakRisk
### StationState
### EVRequest
### BESCOMFeederState
```text
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).
```

### GridState
### EVGridAction
### EVGridObservation
### NegotiationMessage
```text
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.
```

### GridDirective
```text
GridOperator -> FleetDispatcher constraint signal (verifiable).
```

### MultiAgentStepRequest
### MultiAgentStepResponse
### SimTopStation
### SimulationPrediction
```text
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.
```

## Functions

### to_jsonable
### _occupied_le_total
### _check_consistency
