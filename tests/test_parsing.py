import pytest
from ev_grid_oracle.parsing import parse_simulation
from ev_grid_oracle.models import SimTopStation

def test_parse_simulation_valid():
    text = (
        "<SIMULATE>\n"
        "T+5_GRID_LOAD_PCT: 0.85\n"
        "T+5_RENEWABLE_PCT: 0.40\n"
        "T+5_TOP_STATIONS: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1\n"
        "</SIMULATE>\n"
    )
    res = parse_simulation(text)
    assert res is not None
    assert res.t5_grid_load_pct == 0.85
    assert res.t5_renewable_pct == 0.40
    assert len(res.t5_top_stations) == 3
    assert res.t5_top_stations[0].station_id == "BLR-01"
    assert res.t5_top_stations[0].load_pct == 0.82
    assert res.t5_top_stations[0].queue == 3

def test_parse_simulation_missing_match():
    assert parse_simulation("random text") is None

def test_parse_simulation_exception_handling():
    # Provide a malformed tops string to trigger ValueError during parsing
    # Here BLR-01 only has 2 parts when split by ':'
    text1 = (
        "<SIMULATE>\n"
        "T+5_GRID_LOAD_PCT: 0.85\n"
        "T+5_RENEWABLE_PCT: 0.40\n"
        "T+5_TOP_STATIONS: BLR-01:0.82\n"
        "</SIMULATE>\n"
    )
    assert parse_simulation(text1) is None

    # Here load is not a float
    text2 = (
        "<SIMULATE>\n"
        "T+5_GRID_LOAD_PCT: 0.85\n"
        "T+5_RENEWABLE_PCT: 0.40\n"
        "T+5_TOP_STATIONS: BLR-01:abc:3\n"
        "</SIMULATE>\n"
    )
    assert parse_simulation(text2) is None

    # Here queue is not an int
    text3 = (
        "<SIMULATE>\n"
        "T+5_GRID_LOAD_PCT: 0.85\n"
        "T+5_RENEWABLE_PCT: 0.40\n"
        "T+5_TOP_STATIONS: BLR-01:0.82:xyz\n"
        "</SIMULATE>\n"
    )
    assert parse_simulation(text3) is None

    # Missing tops (causes return None, testing branch where tops is empty list)
    text4 = (
        "<SIMULATE>\n"
        "T+5_GRID_LOAD_PCT: 0.85\n"
        "T+5_RENEWABLE_PCT: 0.40\n"
        "T+5_TOP_STATIONS:   \n"
        "</SIMULATE>\n"
    )
    assert parse_simulation(text4) is None
