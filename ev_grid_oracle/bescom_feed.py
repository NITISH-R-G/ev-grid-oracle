from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1
from random import Random

from .models import BESCOMFeederState, GridState


@dataclass(frozen=True, slots=True)
class BESCOMFeedAPI:
    """
    Deterministic BESCOM feeder "API mock".

    - No network calls (HF Spaces safe).
    - Feeder loads are derived from: time-of-day + grid_load_pct + station loads.
    - Output is stable under (seed, scenario, tick) so judge replays match.
    """

    feeder_ids: tuple[str, ...] = ("FDR-NORTH-01", "FDR-SOUTH-01", "FDR-EAST-01", "FDR-WEST-01")

    def snapshot(
        self,
        *,
        state: GridState,
        tick: int,
        scenario: str,
        seed: int,
    ) -> list[BESCOMFeederState]:
        rng = Random(self._stable_seed(seed=seed, scenario=scenario, tick=tick))

        # Zone weights based on station load concentration.
        zone_load: dict[str, float] = {"North": 0.0, "South": 0.0, "East": 0.0, "West": 0.0}
        for s in state.stations:
            z = self._zone_for_station(s.station_id)
            pct = float(s.occupied_slots) / max(1.0, float(s.total_slots))
            zone_load[z] += pct
        # Normalize
        max_z = max(zone_load.values()) if zone_load else 1.0
        if max_z <= 0:
            max_z = 1.0
        zone_load = {k: float(v / max_z) for k, v in zone_load.items()}

        base = float(state.grid_load_pct)
        hour_term = 0.04 * (1.0 if 18 <= int(state.hour) <= 21 else 0.0)  # evening peak bump

        out: list[BESCOMFeederState] = []
        for fid in self.feeder_ids:
            zone = fid.split("-")[1].title()  # NORTH -> North
            z = zone if zone in zone_load else "North"
            jitter = rng.uniform(-0.02, 0.02)
            zterm = (zone_load.get(z, 0.25) - 0.5) * 0.08

            load = min(1.0, max(0.0, base + hour_term + zterm + jitter))

            # Limits: slightly different per zone; tighter in "transformer_derate" family scenarios.
            limit = 0.88 + rng.uniform(-0.015, 0.015)
            if "derate" in scenario or "transformer" in scenario:
                limit -= 0.05
            limit = min(0.95, max(0.78, float(limit)))

            out.append(
                BESCOMFeederState(
                    feeder_id=fid,
                    zone=z,
                    load_pct=float(load),
                    limit_pct=float(limit),
                )
            )

        # Sort stable for prompt readability
        out.sort(key=lambda x: x.feeder_id)
        return out

    def _stable_seed(self, *, seed: int, scenario: str, tick: int) -> int:
        s = f"{seed}:{scenario}:{tick}".encode("utf-8")
        h = sha1(s).hexdigest()[:8]
        return int(h, 16)

    def _zone_for_station(self, station_id: str) -> str:
        # Deterministic mapping; keeps narrative consistent without adding a new data source.
        n = int(station_id.split("-")[1]) if "-" in station_id else 0
        if n % 4 == 0:
            return "East"
        if n % 4 == 1:
            return "South"
        if n % 4 == 2:
            return "West"
        return "North"

