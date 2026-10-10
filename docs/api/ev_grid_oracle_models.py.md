# ev_grid_oracle/models.py

## Class: `ChargerType`

No docstring provided.

## Class: `ChargeRate`

No docstring provided.

## Class: `ActionType`

No docstring provided.

## Class: `DayType`

No docstring provided.

## Class: `PeakRisk`

No docstring provided.

## Class: `StationState`

No docstring provided.

## Class: `EVRequest`

No docstring provided.

## Class: `BESCOMFeederState`

Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

## Class: `GridState`

No docstring provided.

## Class: `EVGridAction`

No docstring provided.

## Class: `EVGridObservation`

No docstring provided.

## Class: `NegotiationMessage`

A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

## Class: `GridDirective`

GridOperator -> FleetDispatcher constraint signal (verifiable).

## Class: `MultiAgentStepRequest`

No docstring provided.

## Class: `MultiAgentStepResponse`

No docstring provided.

## Class: `SimTopStation`

No docstring provided.

## Class: `SimulationPrediction`

Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Function: `to_jsonable`

No docstring provided.
