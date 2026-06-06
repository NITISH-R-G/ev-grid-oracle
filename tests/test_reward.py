from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import ActionType, EVGridAction


def test_reward_breakdown_has_keys_and_total():
    env = EVGridCore(city_graph=build_city_graph())
    obs = env.reset(seed=123)
    if not obs.state.pending_evs:
        obs = env.reset(seed=124)
    ev = obs.state.pending_evs[0]
    action = EVGridAction(action_type=ActionType.defer, ev_id=ev.ev_id, defer_minutes=5)
    obs2 = env.step(action)
    assert "total" in obs2.reward_breakdown
    assert "wait" in obs2.reward_breakdown
    assert "peak" in obs2.reward_breakdown
    assert "renewable" in obs2.reward_breakdown
    assert "urgency" in obs2.reward_breakdown


def test_deferring_critical_ev_penalized():
    env = EVGridCore(city_graph=build_city_graph())
    obs = env.reset(seed=999)
    # force critical + urgent
    if not obs.state.pending_evs:
        obs = env.reset(seed=1000)
    obs.state.pending_evs[0].battery_pct_0_100 = 10.0
    obs.state.pending_evs[0].urgency = 0.95
    ev = obs.state.pending_evs[0]
    action = EVGridAction(action_type=ActionType.defer, ev_id=ev.ev_id, defer_minutes=5)
    obs2 = env.step(action)
    assert obs2.reward_breakdown.get("urgency", 0.0) < 0.0


def test_invalid_station_routes_penalized():
    env = EVGridCore(city_graph=build_city_graph())
    obs = env.reset(seed=321)
    if not obs.state.pending_evs:
        obs = env.reset(seed=322)
    ev = obs.state.pending_evs[0]
    action = EVGridAction(
        action_type=ActionType.route,
        ev_id=ev.ev_id,
        station_id="BLR-99",
        defer_minutes=0,
    )
    obs2 = env.step(action)
    assert obs2.reward_breakdown.get("action/invalid_station", 0.0) < 0.0


from ev_grid_oracle.reward import split_role_rewards


def test_split_role_rewards_exception_handling():
    # Pass a dict where values cannot be cast to float to hit the Exception handler
    from typing import Any

    rb: dict[str, Any] = {
        "wait": "not-a-number",
        "urgency": None,
        "valid_action_shaping": [],
        "anti_hack": {},
        "peak": "invalid",
        "grid_stress": None,
        "renewable": [],
    }

    res = split_role_rewards(rb, grid_directive_ok=True, has_meaningful_messages=True)

    # Check that all keys fall back to 0.0 before any negotiation logic is applied
    # By default, negotiation is 0.25 if both grid_directive_ok and has_meaningful_messages are True
    # fleet["negotiation"] = 0.25 * 0.6 = 0.15
    # grid["negotiation"] = 0.25 * 0.4 = 0.1
    # total for fleet = 0.0 (from 0.0s) + 0.15 = 0.15
    # total for grid = 0.0 (from 0.0s) + 0.1 = 0.1

    fleet = res["fleet"]
    assert fleet["wait"] == 0.0
    assert fleet["urgency"] == 0.0
    assert fleet["valid_action_shaping"] == 0.0
    assert fleet["anti_hack"] == 0.0
    assert fleet["negotiation"] == 0.15
    assert fleet["total"] == 0.15

    grid = res["grid"]
    assert grid["peak"] == 0.0
    assert grid["grid_stress"] == 0.0
    assert grid["renewable"] == 0.0
    assert grid["valid_action_shaping"] == 0.0
    assert grid["anti_hack"] == 0.0
    assert grid["negotiation"] == 0.1
    assert grid["total"] == 0.1

    assert res["joint"]["total"] == 0.25
