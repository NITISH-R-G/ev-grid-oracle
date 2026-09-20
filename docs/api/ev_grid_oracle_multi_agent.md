# Module: `./ev_grid_oracle/multi_agent.py`

**Description:**
*No module docstring provided.*

## Class: `MultiAgentSession`
Minimal explicit multi-agent wrapper around EVGridCore.

- GridOperator emits a directive (constraint signal) + optional message.
- FleetDispatcher emits an action + optional message.
- Resolver applies directive deterministically and steps EVGridCore.

### Method: `MultiAgentSession.step`
*No method docstring provided.*

### Method: `MultiAgentSession.snapshot`
Read-only view of the underlying core state.

