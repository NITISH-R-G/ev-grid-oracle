import pytest

from ev_grid_oracle.city_graph import STATIONS, build_city_graph
from ev_grid_oracle.models import ActionType, EVGridAction


def test_city_graph_connected_and_25_stations():
    g = build_city_graph()
    assert len(STATIONS) == 25
    assert len(g.nodes) == 25


def test_action_route_requires_station_id_and_zero_defer():
    with pytest.raises(Exception):
        EVGridAction(action_type=ActionType.route, ev_id="EV-001", station_id=None, defer_minutes=0)
    with pytest.raises(Exception):
        EVGridAction(action_type=ActionType.route, ev_id="EV-001", station_id="BLR-01", defer_minutes=5)
    ok = EVGridAction(action_type=ActionType.route, ev_id="EV-001", station_id="BLR-01", defer_minutes=0)
    assert ok.station_id == "BLR-01"


def test_action_defer_requires_positive_defer_minutes():
    with pytest.raises(Exception):
        EVGridAction(action_type=ActionType.defer, ev_id="EV-001", defer_minutes=0)
    ok = EVGridAction(action_type=ActionType.defer, ev_id="EV-001", defer_minutes=5)
    assert ok.defer_minutes == 5


def test_time_advances_with_5min_steps():
    from ev_grid_oracle.env import EVGridCore

    core = EVGridCore(city_graph=build_city_graph(), step_minutes=5)
    obs0 = core.reset(seed=123, scenario="baseline")
    h0 = int(obs0.state.hour)
    m0 = int(obs0.state.minute_of_day)

    # 12 steps of 5 minutes = 60 minutes => hour should advance by 1 (mod 24)
    for _ in range(12):
        st = core._grid_state
        ev_id = st.pending_evs[0].ev_id if st and st.pending_evs else "EV-000"
        core.step(EVGridAction(action_type=ActionType.load_shift, ev_id=ev_id, defer_minutes=0))

    obs1 = core.step(EVGridAction(action_type=ActionType.load_shift, ev_id="EV-000", defer_minutes=0))
    h1 = int(obs1.state.hour)
    m1 = int(obs1.state.minute_of_day)
    assert m1 != m0
    assert h1 == ((h0 + 1) % 24)

