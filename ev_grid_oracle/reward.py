from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .models import ActionType, EVGridAction, GridState


@dataclass(frozen=True, slots=True)
class RewardWeights:
    wait: float = 2.0
    grid_stress: float = 3.0
    peak_penalty: float = 15.0
    peak_bonus: float = 2.0
    renewable: float = 1.5

    urgency_ok: float = 3.0
    urgency_defer_penalty: float = 4.0

    impossible: float = 8.0
    queue_piling: float = 3.0


def compute_reward(prev_state: GridState, action: EVGridAction, next_state: GridState) -> tuple[float, dict[str, float]]:
    """
    Deterministic, verifier-style reward with breakdown.

    Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.
    """
    w = RewardWeights()
    r: dict[str, float] = {}

    avg_wait = mean([s.avg_wait_minutes for s in next_state.stations]) if next_state.stations else 0.0
    r["wait"] = -avg_wait * w.wait

    overloaded = sum(1 for s in next_state.stations if (s.occupied_slots / max(1, s.total_slots)) > 0.85)
    r["grid_stress"] = -float(overloaded) * w.grid_stress

    if next_state.grid_load_pct > 0.80:
        r["peak"] = -(next_state.grid_load_pct - 0.80) * w.peak_penalty
    else:
        r["peak"] = (0.80 - next_state.grid_load_pct) * w.peak_bonus

    r["renewable"] = next_state.renewable_pct * w.renewable

    # urgency: never defer high-urgency EVs
    urgency_score = 0.0
    for ev in prev_state.pending_evs:
        if ev.urgency > 0.80:
            if action.ev_id == ev.ev_id and action.action_type != ActionType.defer:
                urgency_score += w.urgency_ok
            elif action.action_type == ActionType.defer:
                urgency_score -= w.urgency_defer_penalty
    r["urgency"] = urgency_score

    # anti-hack penalties
    if action.action_type == ActionType.route:
        station = next((s for s in next_state.stations if s.station_id == action.station_id), None)
        if station is None:
            r["impossible"] = -w.impossible
        else:
            if station.occupied_slots >= station.total_slots:
                r["impossible"] = -w.impossible
            if station.queue_length > 5:
                r["queue_piling"] = -w.queue_piling

    total = float(sum(r.values()))
    return total, r

