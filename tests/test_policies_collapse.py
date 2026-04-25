"""Smoke tests for collapse / stressor policies (deterministic, no env crashes)."""

from __future__ import annotations

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction
from ev_grid_oracle.policies import (
    always_defer_policy,
    always_load_shift_policy,
    baseline_policy,
    nearest_travel_only_policy,
)


def _run_policy(policy_fn, *, seed: int = 11, steps: int = 8) -> None:
    env = EVGridCore(city_graph=build_city_graph())
    obs = env.reset(seed=seed)
    graph = env.city_graph
    for _ in range(steps):
        state = obs.state
        if not state.pending_evs:
            action = EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0)
        else:
            action = policy_fn(state, graph)
        obs = env.step(action)
        if obs.done:
            break


def test_collapse_policies_do_not_crash() -> None:
    for fn in (always_defer_policy, always_load_shift_policy, nearest_travel_only_policy, baseline_policy):
        _run_policy(fn, seed=21, steps=12)


def test_collapse_policies_return_valid_actions_when_pending() -> None:
    env = EVGridCore(city_graph=build_city_graph())
    obs = env.reset(seed=303)
    if not obs.state.pending_evs:
        obs = env.reset(seed=304)
    assert obs.state.pending_evs
    graph = env.city_graph
    for fn in (always_defer_policy, always_load_shift_policy, nearest_travel_only_policy):
        a = fn(obs.state, graph)
        assert a.ev_id
        env.step(a)
