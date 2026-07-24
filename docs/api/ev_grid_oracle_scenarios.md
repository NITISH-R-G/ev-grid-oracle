# Documentation for `./ev_grid_oracle/scenarios.py`

## Classes

### `ScenarioEvent`
*No docstring available.*

### `ScenarioModifiers`
Lightweight knobs applied on top of the core simulator.
These are intentionally simple and deterministic for replayable judging.

## Functions

### `scenario_schedule`
Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

Note: ticks are env steps (5-minute increments by default).

### `apply_scenario_events`
Returns updated modifiers and the list of events that fired this tick.
