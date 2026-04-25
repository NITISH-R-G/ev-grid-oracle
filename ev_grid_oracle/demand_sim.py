from __future__ import annotations

from dataclasses import dataclass
from math import exp
from random import Random


@dataclass(frozen=True, slots=True)
class DemandParams:
    # arrivals per 5-minute step (Poisson mean)
    base_lambda: float = 0.8
    weekday_multiplier: float = 1.0
    weekend_multiplier: float = 0.8

    morning_peak_hour: int = 8
    evening_peak_hour: int = 18
    peak_strength: float = 2.0  # additive bump
    peak_width_hours: float = 2.0


def _gaussian_bump(x: float, mu: float, sigma: float) -> float:
    # unnormalized gaussian bump in [0, ~1]
    if sigma <= 0:
        return 0.0
    z = (x - mu) / sigma
    return exp(-0.5 * z * z)


def expected_arrivals_per_step(hour: int, *, day_type: str, params: DemandParams = DemandParams()) -> float:
    mult = params.weekday_multiplier if day_type == "weekday" else params.weekend_multiplier
    bump = params.peak_strength * (
        _gaussian_bump(hour, params.morning_peak_hour, params.peak_width_hours)
        + _gaussian_bump(hour, params.evening_peak_hour, params.peak_width_hours)
    )
    lam = (params.base_lambda + bump) * mult
    return max(0.0, lam)


def sample_arrivals_per_step(
    rng: Random, hour: int, *, day_type: str, params: DemandParams = DemandParams()
) -> int:
    # Poisson sampler (Knuth) for small lambdas.
    lam = expected_arrivals_per_step(hour, day_type=day_type, params=params)
    if lam <= 0:
        return 0
    l = exp(-lam)
    k = 0
    p = 1.0
    while p > l:
        k += 1
        p *= rng.random()
    return max(0, k - 1)

