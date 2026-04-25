from __future__ import annotations

from dataclasses import dataclass
from math import cos, pi


@dataclass(frozen=True, slots=True)
class GridParams:
    base_load: float = 0.55
    load_amplitude: float = 0.25  # daily swing
    charging_load_per_ev: float = 0.004  # added per occupied slot

    renewable_base: float = 0.18
    renewable_amplitude: float = 0.35  # peaks midday


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def baseline_grid_load(hour: int, *, day_type: str, params: GridParams = GridParams()) -> float:
    # Two-peak-ish load using cosine: highest around evening, lower around midday.
    # Map hour->angle with peak near 18:00.
    angle = 2 * pi * ((hour - 18) / 24.0)
    day_mult = 1.0 if day_type == "weekday" else 0.9
    load = params.base_load + params.load_amplitude * (0.5 + 0.5 * cos(angle))
    return _clamp01(load * day_mult)


def renewable_pct(hour: int, params: GridParams = GridParams()) -> float:
    # Midday solar bump: peak around 13:00, low at night.
    angle = 2 * pi * ((hour - 13) / 24.0)
    ren = params.renewable_base + params.renewable_amplitude * (0.5 + 0.5 * cos(angle))
    return _clamp01(ren)


def update_grid_load(
    *,
    hour: int,
    day_type: str,
    occupied_slots_total: int,
    load_shift_action_strength: float = 0.0,
    params: GridParams = GridParams(),
) -> tuple[float, float]:
    base = baseline_grid_load(hour, day_type=day_type, params=params)
    added = occupied_slots_total * params.charging_load_per_ev
    load = _clamp01(base + added - load_shift_action_strength)
    ren = renewable_pct(hour, params=params)
    return load, ren

