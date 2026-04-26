from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .env import EVGridCore
from .models import ActionType, EVGridAction, GridDirective, NegotiationMessage
from .policies import baseline_policy


@dataclass
class MultiAgentSession:
    """
    Minimal explicit multi-agent wrapper around EVGridCore.

    - GridOperator emits a directive (constraint signal) + optional message.
    - FleetDispatcher emits an action + optional message.
    - Resolver applies directive deterministically and steps EVGridCore.
    """

    core: EVGridCore
    messages: list[NegotiationMessage] = field(default_factory=list)
    last_directive: GridDirective = field(default_factory=GridDirective)
    last_resolved_action: EVGridAction | None = None
    last_violations: list[str] = field(default_factory=list)

    def step(
        self,
        *,
        grid_directive: GridDirective,
        fleet_action: EVGridAction,
        grid_message: NegotiationMessage | None,
        fleet_message: NegotiationMessage | None,
    ) -> EVGridAction:
        self.last_directive = grid_directive
        self.last_violations = []

        if grid_message is not None:
            self.messages.append(grid_message)
        if fleet_message is not None:
            self.messages.append(fleet_message)

        resolved = fleet_action

        # Directive enforcement v0:
        # - blacklist stations (force reroute)
        # - apply price multiplier via scenario modifiers indirectly (handled in EVGridCore via tariffs)
        # - if action would exceed critical grid load budget, force load_shift (soft constraint)
        st = self.core._grid_state
        if st is not None:
            if resolved.action_type.value == "route" and resolved.station_id in set(grid_directive.station_blacklist):
                self.last_violations.append("station_blacklist")
                # Deterministic reroute: baseline policy chooses the best allowed station.
                resolved = baseline_policy(st, self.core.city_graph)

            # If grid is already above budget, steer away from routing into more load:
            if float(st.grid_load_pct) >= float(grid_directive.max_grid_load_pct):
                if resolved.action_type.value == "route":
                    self.last_violations.append("grid_budget_exceeded")
                    resolved = EVGridAction(action_type=ActionType.load_shift, ev_id=resolved.ev_id, defer_minutes=0)

        self.last_resolved_action = resolved
        self.core.step(resolved)
        return resolved

    def snapshot(self) -> dict[str, Any]:
        """
        Read-only view of the underlying core state.
        """
        st = self.core._grid_state
        return {} if st is None else st.model_dump(mode="json")

