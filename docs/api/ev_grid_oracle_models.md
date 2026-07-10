# ev_grid_oracle/models.py

## Class `ChargerType`

## Class `ChargeRate`

## Class `ActionType`

## Class `DayType`

## Class `PeakRisk`

## Class `StationState`

### Method `_occupied_le_total`

## Class `EVRequest`

## Class `BESCOMFeederState`

Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

## Class `GridState`

## Class `EVGridAction`

### Method `_check_consistency`

## Class `EVGridObservation`

## Class `NegotiationMessage`

A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

## Class `GridDirective`

GridOperator -> FleetDispatcher constraint signal (verifiable).

## Class `MultiAgentStepRequest`

## Class `MultiAgentStepResponse`

## Class `SimTopStation`

## Class `SimulationPrediction`

Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Function `to_jsonable`

## Function `_occupied_le_total`

## Function `_check_consistency`
