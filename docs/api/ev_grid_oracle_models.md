# API Reference for `./ev_grid_oracle/models.py`

## Class: `ChargerType`

No docstring available.

## Class: `ChargeRate`

No docstring available.

## Class: `ActionType`

No docstring available.

## Class: `DayType`

No docstring available.

## Class: `PeakRisk`

No docstring available.

## Class: `StationState`

No docstring available.

## Class: `EVRequest`

No docstring available.

## Class: `BESCOMFeederState`

Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

## Class: `GridState`

No docstring available.

## Class: `EVGridAction`

No docstring available.

## Class: `EVGridObservation`

No docstring available.

## Class: `NegotiationMessage`

A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

## Class: `GridDirective`

GridOperator -> FleetDispatcher constraint signal (verifiable).

## Class: `MultiAgentStepRequest`

No docstring available.

## Class: `MultiAgentStepResponse`

No docstring available.

## Class: `SimTopStation`

No docstring available.

## Class: `SimulationPrediction`

Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Function: `to_jsonable`

No docstring available.

## Function: `_occupied_le_total`

No docstring available.

## Function: `_check_consistency`

No docstring available.
