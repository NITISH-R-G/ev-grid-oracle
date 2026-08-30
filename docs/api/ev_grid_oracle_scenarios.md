# Documentation for `ev_grid_oracle/scenarios.py`

## Classes

### Class `ScenarioEvent`

No documentation provided.

### Class `ScenarioModifiers`

Lightweight knobs applied on top of the core simulator.
These are intentionally simple and deterministic for replayable judging.

## Functions

### Function `scenario_schedule`

Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

Note: ticks are env steps (5-minute increments by default).

### Function `apply_scenario_events`

Returns updated modifiers and the list of events that fired this tick.
