from ev_grid_oracle.models import ActionType, ChargeRate
from ev_grid_oracle.parsing import (
    parse_simulation,
    parse_action,
    parse_simulation_and_action,
)


def test_parse_simulation():
    # Happy path
    valid_text = """
Some prior context...
<SIMULATE>
T+5_GRID_LOAD_PCT: 0.85
T+5_RENEWABLE_PCT: 0.42
T+5_TOP_STATIONS: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1
</SIMULATE>
Other stuff...
"""
    sim = parse_simulation(valid_text)
    assert sim is not None
    assert sim.t5_grid_load_pct == 0.85
    assert sim.t5_renewable_pct == 0.42
    assert len(sim.t5_top_stations) == 3
    assert sim.t5_top_stations[0].station_id == "BLR-01"
    assert sim.t5_top_stations[0].load_pct == 0.82
    assert sim.t5_top_stations[0].queue == 3

    # Missing simulation block
    assert parse_simulation("No simulation here") is None

    # Missing closing tag (no match)
    incomplete_text = """
    <SIMULATE>
    T+5_GRID_LOAD_PCT: 0.85
    T+5_RENEWABLE_PCT: 0.42
    T+5_TOP_STATIONS: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1
    """
    assert parse_simulation(incomplete_text) is None

    # Invalid grid load (triggers exception in parsing floats)
    invalid_grid_text = """
    <SIMULATE>
    T+5_GRID_LOAD_PCT: NOT_A_FLOAT
    T+5_RENEWABLE_PCT: 0.42
    T+5_TOP_STATIONS: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1
    </SIMULATE>
    """
    # Because of regex `[01](?:\.\d+)?` NOT_A_FLOAT won't even match
    assert parse_simulation(invalid_grid_text) is None

    # Try an invalid value that still matches regex roughly (like missing tops)
    # The regex requires tops. If tops doesn't have the expected parts, it'll raise exception during parsing
    invalid_tops_text = """
    <SIMULATE>
    T+5_GRID_LOAD_PCT: 0.85
    T+5_RENEWABLE_PCT: 0.42
    T+5_TOP_STATIONS: BLR-01:0.82_missing_parts
    </SIMULATE>
    """
    assert parse_simulation(invalid_tops_text) is None


def test_parse_action():
    # Route action
    route_text = "ACTION: route\nSTATION: BLR-01\nCHARGE_RATE: fast\nDEFER_MINUTES: 0\n"
    action = parse_action(route_text, ev_id="EV-1")
    assert action is not None
    assert action.action_type == ActionType.route
    assert action.station_id == "BLR-01"
    assert action.charge_rate == ChargeRate.fast
    assert action.defer_minutes == 0

    # Defer action
    defer_text = "ACTION: defer\nSTATION: NONE\nCHARGE_RATE: fast\nDEFER_MINUTES: 30\n"
    action = parse_action(defer_text, ev_id="EV-1")
    assert action is not None
    assert action.action_type == ActionType.defer
    assert action.station_id is None
    assert action.defer_minutes == 30

    # Load shift action
    load_shift_text = (
        "ACTION: load_shift\nSTATION: NONE\nCHARGE_RATE: slow\nDEFER_MINUTES: 0\n"
    )
    action = parse_action(load_shift_text, ev_id="EV-1")
    assert action is not None
    assert action.action_type == ActionType.load_shift
    assert action.station_id is None
    assert action.charge_rate == ChargeRate.slow

    # Missing action
    assert parse_action("No action here", ev_id="EV-1") is None

    # Validation exception - route missing station_id (NONE instead of a valid ID)
    invalid_route_text = (
        "ACTION: route\nSTATION: NONE\nCHARGE_RATE: fast\nDEFER_MINUTES: 0\n"
    )
    assert parse_action(invalid_route_text, ev_id="EV-1") is None

    # Validation exception - defer with 0 minutes
    invalid_defer_text = (
        "ACTION: defer\nSTATION: NONE\nCHARGE_RATE: fast\nDEFER_MINUTES: 0\n"
    )
    assert parse_action(invalid_defer_text, ev_id="EV-1") is None

    # Validation exception - load_shift with defer_minutes != 0
    invalid_load_shift_text = (
        "ACTION: load_shift\nSTATION: NONE\nCHARGE_RATE: fast\nDEFER_MINUTES: 10\n"
    )
    assert parse_action(invalid_load_shift_text, ev_id="EV-1") is None


def test_parse_simulation_and_action():
    valid_sim = """
<SIMULATE>
T+5_GRID_LOAD_PCT: 0.85
T+5_RENEWABLE_PCT: 0.42
T+5_TOP_STATIONS: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1
</SIMULATE>
"""
    valid_act = "ACTION: route\nSTATION: BLR-01\nCHARGE_RATE: fast\nDEFER_MINUTES: 0\n"

    # Both
    sim, act = parse_simulation_and_action(valid_sim + valid_act, ev_id="EV-1")
    assert sim is not None
    assert act is not None

    # Only sim
    sim, act = parse_simulation_and_action(valid_sim, ev_id="EV-1")
    assert sim is not None
    assert act is None

    # Only act
    sim, act = parse_simulation_and_action(valid_act, ev_id="EV-1")
    assert sim is None
    assert act is not None

    # Neither
    sim, act = parse_simulation_and_action("Just talking here", ev_id="EV-1")
    assert sim is None
    assert act is None
