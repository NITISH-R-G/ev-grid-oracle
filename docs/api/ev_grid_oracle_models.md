# Module: `./ev_grid_oracle/models.py`

**Description:**
*No module docstring provided.*

## Class: `ChargerType`
*No class docstring provided.*

## Class: `ChargeRate`
*No class docstring provided.*

## Class: `ActionType`
*No class docstring provided.*

## Class: `DayType`
*No class docstring provided.*

## Class: `PeakRisk`
*No class docstring provided.*

## Class: `StationState`
*No class docstring provided.*

### Method: `StationState._occupied_le_total`
*No method docstring provided.*

## Class: `EVRequest`
*No class docstring provided.*

## Class: `BESCOMFeederState`
Lightweight, judge-friendly feeder snapshot (mocked but deterministic).

## Class: `GridState`
*No class docstring provided.*

## Class: `EVGridAction`
*No class docstring provided.*

### Method: `EVGridAction._check_consistency`
*No method docstring provided.*

## Class: `EVGridObservation`
*No class docstring provided.*

## Class: `NegotiationMessage`
A short, bounded message used in the explicit multi-agent protocol.

This is *not* a free-form chat reward. It exists so judges can see
negotiation/constraints explicitly and we can penalize empty spam.

## Class: `GridDirective`
GridOperator -> FleetDispatcher constraint signal (verifiable).

## Class: `MultiAgentStepRequest`
*No class docstring provided.*

## Class: `MultiAgentStepResponse`
*No class docstring provided.*

## Class: `SimTopStation`
*No class docstring provided.*

## Class: `SimulationPrediction`
Aggregated 'dream state' prediction for T+5 ticks.
Kept intentionally small and verifiable for hackathon judging.

## Function: `to_jsonable`
*No function docstring provided.*

