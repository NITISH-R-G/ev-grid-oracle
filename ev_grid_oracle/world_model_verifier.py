from __future__ import annotations

import copy
from dataclasses import dataclass
from statistics import mean

from .env import _apply_action, _drain_queues_and_charging, _peak_risk, _update_station_waits
from .grid_sim import update_grid_load
from .models import EVGridAction, GridState, SimulationPrediction


@dataclass(frozen=True, slots=True)
class PredictionScore:
    score_0_1: float
    breakdown: dict[str, float]


def _top3(st: GridState) -> list[tuple[str, float, int]]:
    rows = []
    for s in st.stations:
        load = s.occupied_slots / max(1, s.total_slots)
        rows.append((s.station_id, float(load), int(s.queue_length)))
    rows.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return rows[:3]


def rollout_deterministic_5ticks(prev_state: GridState, action: EVGridAction) -> GridState:
    """
    Deterministic verifier rollout: apply action once, then advance 5 ticks with *no new arrivals*.
    This is intentionally verifier-friendly (stable + reproducible) for RLVR.
    """
    st = copy.deepcopy(prev_state)

    # tick 0: apply proposed action
    _apply_action(st, action)

    for _ in range(5):
        # drain queues / charging (deterministic)
        _drain_queues_and_charging(st)
        # grid update (deterministic function of hour/day/occupied)
        occupied_total = sum(s.occupied_slots for s in st.stations)
        load_shift_strength = 0.03 if action.action_type.value == "load_shift" else 0.0
        grid_load, renewable = update_grid_load(
            hour=st.hour,
            day_type=st.day_type.value,
            occupied_slots_total=occupied_total,
            load_shift_action_strength=load_shift_strength,
        )
        st.grid_load_pct = grid_load
        st.renewable_pct = renewable
        st.peak_risk = _peak_risk(grid_load)
        _update_station_waits(st, step_minutes=5)
    return st


def score_prediction(prev_state: GridState, action: EVGridAction, pred: SimulationPrediction) -> PredictionScore:
    """
    Score dream-state prediction accuracy against a deterministic T+5 verifier rollout.
    Returns score in [0,1].
    """
    next5 = rollout_deterministic_5ticks(prev_state, action)

    # grid/renew MAE
    grid_err = abs(pred.t5_grid_load_pct - next5.grid_load_pct)
    ren_err = abs(pred.t5_renewable_pct - next5.renewable_pct)

    # station top-3 match: compare ids and values
    top_true = _top3(next5)
    true_ids = {sid for sid, _, _ in top_true}
    pred_ids = {t.station_id for t in pred.t5_top_stations}
    jacc = len(true_ids & pred_ids) / max(1, len(true_ids | pred_ids))

    # for overlap, compare load/queue
    by_true = {sid: (load, q) for sid, load, q in top_true}
    overlaps = []
    for t in pred.t5_top_stations:
        if t.station_id in by_true:
            load_t, q_t = by_true[t.station_id]
            overlaps.append(abs(t.load_pct - load_t) + abs(t.queue - q_t) / 10.0)
    overlap_err = mean(overlaps) if overlaps else 1.0

    # Convert to score: smaller error -> higher score.
    # Keep bounded and interpretable.
    grid_score = max(0.0, 1.0 - (grid_err / 0.25))
    ren_score = max(0.0, 1.0 - (ren_err / 0.25))
    overlap_score = max(0.0, 1.0 - overlap_err)

    score = 0.40 * grid_score + 0.25 * ren_score + 0.20 * jacc + 0.15 * overlap_score
    score = 0.0 if score < 0.0 else 1.0 if score > 1.0 else score
    return PredictionScore(
        score_0_1=float(score),
        breakdown={
            "pred/grid_score": float(grid_score),
            "pred/renew_score": float(ren_score),
            "pred/top3_jaccard": float(jacc),
            "pred/top3_value_score": float(overlap_score),
        },
    )

