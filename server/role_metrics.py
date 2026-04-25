from __future__ import annotations

from typing import Any

from ev_grid_oracle.models import EVGridAction, EVGridObservation

Role = str  # "discom" | "cpo" | "fleet" | "driver"


def compute_role_kpis(obs: EVGridObservation) -> dict[Role, dict[str, float]]:
    st = obs.state
    avg_wait = (
        sum(s.avg_wait_minutes for s in st.stations) / max(1, len(st.stations)) if st.stations else 0.0
    )
    max_queue = float(max((s.queue_length for s in st.stations), default=0))
    max_occ = float(max((s.occupied_slots / max(1, s.total_slots) for s in st.stations), default=0.0))
    pending = len(st.pending_evs)
    top_urgency = float(max((ev.urgency for ev in st.pending_evs), default=0.0))

    return {
        "discom": {
            "grid_load_pct": float(st.grid_load_pct),
            "renewable_pct": float(st.renewable_pct),
            "peak_risk_score": _peak_risk_score(st.peak_risk.value),
        },
        "cpo": {
            "max_station_occupancy": float(max_occ),
            "max_queue": float(max_queue),
            "avg_wait_minutes": float(avg_wait),
        },
        "fleet": {
            "pending_evs": float(pending),
            "top_urgency": float(top_urgency),
        },
        "driver": {
            "avg_wait_minutes": float(avg_wait),
            "max_queue": float(max_queue),
        },
    }


def compute_role_reward_breakdown(obs: EVGridObservation) -> dict[Role, dict[str, float]]:
    """
    Lightweight, explainable credit assignment for demo storytelling.

    This is NOT a full MARL credit assignment — it allocates the *same* component
    values across roles with fixed weights so totals remain easy to interpret.
    """
    rb = obs.reward_breakdown or {}
    keys = ["wait", "grid_stress", "peak", "renewable", "urgency", "anti_hack", "valid_action_shaping"]

    def part(key: str) -> float:
        v = rb.get(key, 0.0)
        try:
            return float(v)
        except Exception:
            return 0.0

    comps = {k: part(k) for k in keys}

    # Role weights per component (rows sum ~1 per component; values are illustrative).
    weights: dict[str, dict[Role, float]] = {
        "wait": {"discom": 0.10, "cpo": 0.55, "fleet": 0.20, "driver": 0.15},
        "grid_stress": {"discom": 0.65, "cpo": 0.25, "fleet": 0.05, "driver": 0.05},
        "peak": {"discom": 0.80, "cpo": 0.10, "fleet": 0.05, "driver": 0.05},
        "renewable": {"discom": 0.70, "cpo": 0.05, "fleet": 0.15, "driver": 0.10},
        "urgency": {"discom": 0.05, "cpo": 0.05, "fleet": 0.70, "driver": 0.20},
        "anti_hack": {"discom": 0.35, "cpo": 0.35, "fleet": 0.20, "driver": 0.10},
        "valid_action_shaping": {"discom": 0.15, "cpo": 0.15, "fleet": 0.40, "driver": 0.30},
    }

    out: dict[Role, dict[str, float]] = {r: {k: 0.0 for k in keys} for r in ("discom", "cpo", "fleet", "driver")}
    for k in keys:
        wmap = weights.get(k, {})
        for r in out.keys():
            out[r][k] = float(comps[k]) * float(wmap.get(r, 0.0))

    totals: dict[Role, float] = {}
    for r, m in out.items():
        totals[r] = float(sum(m.values()))
    for r, t in totals.items():
        out[r]["total"] = t

    return out


def _peak_risk_score(peak_risk: str) -> float:
    return {"low": 0.0, "medium": 0.33, "high": 0.66, "critical": 1.0}.get(peak_risk, 0.0)


def summarize_action(action: EVGridAction) -> dict[str, Any]:
    return action.model_dump(mode="json")
