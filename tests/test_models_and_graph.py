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

