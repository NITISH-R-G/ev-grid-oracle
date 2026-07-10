# ev_grid_oracle/multi_agent.py

## Class `MultiAgentSession`

Minimal explicit multi-agent wrapper around EVGridCore.

- GridOperator emits a directive (constraint signal) + optional message.
- FleetDispatcher emits an action + optional message.
- Resolver applies directive deterministically and steps EVGridCore.

### Method `step`

### Method `snapshot`

Read-only view of the underlying core state.

## Function `step`

## Function `snapshot`

Read-only view of the underlying core state.
