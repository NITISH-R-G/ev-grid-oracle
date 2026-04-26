from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Literal


def _clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _stable_u01(*parts: object) -> float:
    """
    Stable pseudo-random in [0,1) from input parts.
    Deterministic across processes and Python versions.
    """
    s = "|".join(str(p) for p in parts).encode("utf-8")
    h = hashlib.sha1(s).digest()
    # 53-bit mantissa for stable float-like behavior
    n = int.from_bytes(h[:8], "big") >> 11
    return n / float(1 << 53)


@dataclass(frozen=True)
class TrafficModel:
    """
    Deterministic synthetic traffic for hackathon demos.

    Returns a multiplier m in [0.35, 1.15] to scale base travel_s on an edge.
    """

    seed: int
    scenario: str

    def multiplier_for_edge(self, *, u: int, v: int, mid_lat: float, mid_lng: float, tick: int) -> float:
        # Base: stable per-edge noise, gently time-modulated.
        base = _stable_u01(self.seed, self.scenario, "edge", min(u, v), max(u, v))
        t = tick / 12.0
        wobble = 0.5 + 0.5 * math.sin(t + base * math.tau)

        # 2 moving hotspots (corridors), deterministic from seed+scenario.
        # Hotspot centers drift slowly; intensity depends on distance in lat/lng space.
        def hotspot(k: int) -> float:
            a = _stable_u01(self.seed, self.scenario, "hot", k, "a")
            b = _stable_u01(self.seed, self.scenario, "hot", k, "b")
            c = _stable_u01(self.seed, self.scenario, "hot", k, "c")
            # Drift amplitudes tuned to Bangalore bbox scale (roughly).
            lat0 = 12.93 + (a - 0.5) * 0.22
            lng0 = 77.58 + (b - 0.5) * 0.28
            lat = lat0 + 0.06 * math.sin(0.07 * tick + a * math.tau)
            lng = lng0 + 0.08 * math.cos(0.06 * tick + b * math.tau)
            # Distance proxy (not haversine, cheaper, good enough for visual realism)
            d2 = ((mid_lat - lat) / 0.07) ** 2 + ((mid_lng - lng) / 0.09) ** 2
            inten = math.exp(-d2)
            # Scenario modulation
            s_mod = 1.0
            if "Monsoon" in self.scenario:
                s_mod = 1.15
            if "Cricket" in self.scenario:
                s_mod = 1.08
            return inten * (0.25 + 0.35 * c) * s_mod

        hot = hotspot(0) + hotspot(1)

        # Convert into multiplier: higher hot/wobble => slower (bigger multiplier).
        # Keep mid around 1.0 with bounded range.
        m = 0.85 + 0.18 * wobble + 0.55 * hot + 0.08 * (base - 0.5)
        return _clamp(m, 0.35, 1.15)

