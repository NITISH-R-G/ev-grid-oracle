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
    action = EVGridAction(action_type=ActionType.route, ev_id=ev.ev_id, station_id="BLR-99", defer_minutes=0)
    obs2 = env.step(action)
    assert obs2.reward_breakdown.get("action/invalid_station", 0.0) < 0.0

