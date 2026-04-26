"""Determinism + strict action validation (core env, no LLM)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction
from ev_grid_oracle.policies import baseline_policy


def test_reset_state_identical_two_cores_same_seed() -> None:
    g = build_city_graph()
    a = EVGridCore(city_graph=g)
    b = EVGridCore(city_graph=g)
    oa = a.reset(seed=4242, scenario="festival_surge", fleet_mode="mixed")
    ob = b.reset(seed=4242, scenario="festival_surge", fleet_mode="mixed")
    assert oa.state.model_dump() == ob.state.model_dump()


def test_step_sequence_identical_two_cores_same_actions() -> None:
    g = build_city_graph()
    env_a = EVGridCore(city_graph=g)
    env_b = EVGridCore(city_graph=g)
    obs_a = env_a.reset(seed=7, scenario="baseline", fleet_mode="taxi")
    obs_b = env_b.reset(seed=7, scenario="baseline", fleet_mode="taxi")
    assert obs_a.state.model_dump() == obs_b.state.model_dump()

    for _ in range(6):
        act = baseline_policy(obs_a.state, g)
        assert isinstance(act, EVGridAction)
        oa = env_a.step(act)
        ob = env_b.step(act)
        assert oa.state.model_dump() == ob.state.model_dump()
        assert oa.done == ob.done
        obs_a = oa


@pytest.mark.parametrize(
    "payload",
    [
        {"action_type": "route", "ev_id": "EV-1"},
        {"action_type": "not_an_action", "ev_id": "EV-1", "station_id": "BLR-01"},
        {},
    ],
)
def test_ev_grid_action_rejects_malformed_payload(payload: dict) -> None:
    with pytest.raises(ValidationError):
        EVGridAction.model_validate(payload)


def test_route_action_requires_station() -> None:
    with pytest.raises(ValidationError):
        EVGridAction(action_type=ActionType.route, ev_id="EV-1", station_id=None, defer_minutes=0)
