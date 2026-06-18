import math
from ev_grid_oracle.grid_sim import (
    GridParams,
    _clamp01,
    baseline_grid_load,
    renewable_pct,
    update_grid_load,
)


def test_clamp01():
    assert _clamp01(0.5) == 0.5
    assert _clamp01(-0.1) == 0.0
    assert _clamp01(1.1) == 1.0
    assert _clamp01(0.0) == 0.0
    assert _clamp01(1.0) == 1.0


def test_baseline_grid_load():
    params = GridParams(base_load=0.5, load_amplitude=0.2)

    # 18:00 is peak: angle = 0, cos(0) = 1
    # expected = 0.5 + 0.2 * (0.5 + 0.5 * 1) = 0.5 + 0.2 = 0.7
    load_peak_weekday = baseline_grid_load(18, day_type="weekday", params=params)
    assert math.isclose(load_peak_weekday, 0.7)

    # Non-weekday applies 0.9 multiplier
    load_peak_weekend = baseline_grid_load(18, day_type="weekend", params=params)
    assert math.isclose(load_peak_weekend, 0.7 * 0.9)

    # 6:00 is trough: angle = 2*pi*(-12/24) = -pi, cos(-pi) = -1
    # expected = 0.5 + 0.2 * (0.5 + 0.5 * -1) = 0.5 + 0 = 0.5
    load_trough_weekday = baseline_grid_load(6, day_type="weekday", params=params)
    assert math.isclose(load_trough_weekday, 0.5)


def test_baseline_grid_load_clamping():
    params = GridParams(base_load=1.5, load_amplitude=0.5)
    load = baseline_grid_load(18, day_type="weekday", params=params)
    assert load == 1.0  # Should be clamped to 1.0


def test_renewable_pct():
    params = GridParams(renewable_base=0.1, renewable_amplitude=0.4)

    # 13:00 is peak: angle = 0, cos(0) = 1
    # expected = 0.1 + 0.4 * (0.5 + 0.5 * 1) = 0.1 + 0.4 = 0.5
    ren_peak = renewable_pct(13, params=params)
    assert math.isclose(ren_peak, 0.5)

    # 1:00 is trough: angle = 2*pi*(-12/24) = -pi, cos(-pi) = -1
    # expected = 0.1 + 0.4 * (0.5 + 0.5 * -1) = 0.1 + 0 = 0.1
    ren_trough = renewable_pct(1, params=params)
    assert math.isclose(ren_trough, 0.1)


def test_renewable_pct_clamping():
    params = GridParams(renewable_base=0.8, renewable_amplitude=0.5)
    ren = renewable_pct(13, params=params)
    assert ren == 1.0  # Should be clamped to 1.0


def test_update_grid_load():
    params = GridParams(
        base_load=0.5,
        load_amplitude=0.0,  # disable amplitude for simpler test
        charging_load_per_ev=0.01,
        renewable_base=0.2,
        renewable_amplitude=0.0,  # disable amplitude for simpler test
    )

    # Base load is 0.5. Occupied slots=10 means added=0.1.
    # Total expected load = 0.5 + 0.1 = 0.6
    load, ren = update_grid_load(
        hour=12,
        day_type="weekday",
        occupied_slots_total=10,
        load_shift_action_strength=0.0,
        params=params,
    )
    assert math.isclose(load, 0.6)
    assert math.isclose(ren, 0.2)

    # Test load shifting subtraction
    load_shifted, _ = update_grid_load(
        hour=12,
        day_type="weekday",
        occupied_slots_total=10,
        load_shift_action_strength=0.15,
        params=params,
    )
    assert math.isclose(load_shifted, 0.45)


def test_update_grid_load_clamping():
    params = GridParams(
        base_load=0.9,
        load_amplitude=0.0,
        charging_load_per_ev=0.05,
    )
    # Total expected load before clamp = 0.9 + (10 * 0.05) = 1.4 -> clamps to 1.0
    load, _ = update_grid_load(
        hour=12,
        day_type="weekday",
        occupied_slots_total=10,
        load_shift_action_strength=0.0,
        params=params,
    )
    assert load == 1.0
