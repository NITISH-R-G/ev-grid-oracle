from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

import networkx as nx

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

    anti_hack_base: float = 6.0
    teleportation: float = 10.0
    time_window_violation: float = 6.0
    grid_limit_violation: float = 8.0

    valid_action_shaping: float = 0.1


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    # small, dependency-free distance estimate for anti-cheat checks
    from math import asin, cos, radians, sin, sqrt

    r = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(p1) * cos(p2) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return float(r * c)


def _graph_route_km(city_graph: nx.Graph, lat1: float, lng1: float, lat2: float, lng2: float) -> float | None:
    """
    Approximate driving distance along the city graph using haversine edge weights.
    Returns None if no path exists.
    """
    try:
        n1 = min(city_graph.nodes, key=lambda n: _haversine_km(lat1, lng1, float(n[0]), float(n[1])))
        n2 = min(city_graph.nodes, key=lambda n: _haversine_km(lat2, lng2, float(n[0]), float(n[1])))

        path = nx.shortest_path(city_graph, n1, n2, weight="km")
        total = 0.0
        for a, b in zip(path, path[1:]):
            w = city_graph[a][b].get("km")
            if w is None:
                total += _haversine_km(float(a[0]), float(a[1]), float(b[0]), float(b[1]))
            else:
                total += float(w)
        return float(total)
    except Exception:
        return None


def compute_reward(
    *,
    prev_state: GridState,
    action: EVGridAction,
    next_state: GridState,
    city_graph: nx.Graph,
    step_minutes: int,
) -> tuple[float, dict[str, float], list[str], dict[str, str]]:
    """
    Deterministic, verifier-style reward with breakdown.

    Matches hackathon spec: wait, grid_stress, peak, renewable, urgency, anti-hack.
    """
    w = RewardWeights()
    r: dict[str, float] = {}
    flags: list[str] = []
    details: dict[str, str] = {}

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

    # anti-hack penalties + flags (deterministic)
    r["anti_hack"] = 0.0
    r["valid_action_shaping"] = 0.0

    def add_flag(flag: str, detail: str) -> None:
        if flag not in flags:
            flags.append(flag)
        details[flag] = detail

    # baseline shaping: valid actions get a tiny positive signal (helps learning stability)
    shaping_ok = True

    if action.action_type == ActionType.route:
        station = next((s for s in next_state.stations if s.station_id == action.station_id), None)
        ev = next((e for e in prev_state.pending_evs if e.ev_id == action.ev_id), None)
        src = next((s for s in prev_state.stations if s.neighborhood_slug == (ev.neighborhood_slug if ev else "")), None)

        if station is None:
            r["anti_hack"] -= w.anti_hack_base
            add_flag("phantom_capacity", f"Unknown station_id={action.station_id!r}")
            shaping_ok = False
        elif ev is None:
            r["anti_hack"] -= w.anti_hack_base
            add_flag("phantom_capacity", f"Unknown ev_id={action.ev_id!r}")
            shaping_ok = False
        elif src is None:
            r["anti_hack"] -= w.anti_hack_base
            add_flag("phantom_capacity", "Could not resolve EV neighborhood to a station anchor")
            shaping_ok = False
        else:
            # Feasibility: SOC must be able to reach station (very rough range model)
            dist_km = _graph_route_km(city_graph, src.lat, src.lng, station.lat, station.lng)
            if dist_km is None:
                dist_km = _haversine_km(src.lat, src.lng, station.lat, station.lng)

            # ~6 km per 1% SOC (tunable coarse proxy)
            required_soc = dist_km / 6.0
            if float(ev.battery_pct_0_100) + 1e-6 < float(required_soc):
                r["anti_hack"] -= w.teleportation
                add_flag(
                    "teleportation",
                    f"Insufficient SOC for distance: battery={ev.battery_pct_0_100:.1f}% needs~{required_soc:.1f}% for ~{dist_km:.1f}km",
                )
                shaping_ok = False

            # Capacity / queue piling
            if station.occupied_slots >= station.total_slots:
                r["anti_hack"] -= w.impossible
                add_flag("phantom_capacity", f"Station full: {station.station_id} occupied={station.occupied_slots}/{station.total_slots}")
                shaping_ok = False
            if station.queue_length > 5:
                r["anti_hack"] -= w.queue_piling
                add_flag("queue_piling", f"Queue too long at {station.station_id}: {station.queue_length}")
                shaping_ok = False

            # Grid limit violation (post-action world stress)
            if float(next_state.grid_load_pct) >= 0.92:
                r["anti_hack"] -= w.grid_limit_violation
                add_flag("grid_limit_violation", f"Grid load critical: {next_state.grid_load_pct*100:.1f}%")
                shaping_ok = False

    if action.action_type == ActionType.defer:
        ev = next((e for e in prev_state.pending_evs if e.ev_id == action.ev_id), None)
        if ev is not None and int(action.defer_minutes) > int(ev.max_wait_minutes):
            r["anti_hack"] -= w.time_window_violation
            add_flag(
                "time_window_violation",
                f"defer_minutes={action.defer_minutes} exceeds max_wait_minutes={ev.max_wait_minutes}",
            )
            shaping_ok = False

    if shaping_ok:
        r["valid_action_shaping"] = w.valid_action_shaping

    # NOTE: `total` is returned separately; callers may merge additional float debug keys
    # (e.g. `action/*`) into the breakdown dict before setting `total`.
    total = float(sum(v for k, v in r.items() if not k.startswith("_")))
    return total, r, flags, details


def split_role_rewards(rb: dict[str, float], *, grid_directive_ok: bool, has_meaningful_messages: bool) -> dict[str, dict[str, float]]:
    """
    Deterministic role-level reward views derived from the same underlying breakdown.

    This is intentionally simple and bounded (judge-friendly): it does not claim
    full MARL credit assignment, but it does make incentives explicit.
    """
    def f(x: str) -> float:
        try:
            return float(rb.get(x, 0.0))
        except Exception:
            return 0.0

    fleet = {
        "wait": f("wait"),
        "urgency": f("urgency"),
        "valid_action_shaping": f("valid_action_shaping"),
        "anti_hack": f("anti_hack"),
    }
    grid = {
        "peak": f("peak"),
        "grid_stress": f("grid_stress"),
        "renewable": f("renewable"),
        "valid_action_shaping": 0.0,
        "anti_hack": f("anti_hack"),
    }

    # Negotiation verifier (bounded): small bonus only when both sides participate
    # and the dispatcher respected the directive.
    nego = 0.0
    if has_meaningful_messages and grid_directive_ok:
        nego = 0.25
    elif has_meaningful_messages and not grid_directive_ok:
        nego = -0.25
    fleet["negotiation"] = nego * 0.6
    grid["negotiation"] = nego * 0.4

    fleet["total"] = float(sum(v for k, v in fleet.items() if k != "total"))
    grid["total"] = float(sum(v for k, v in grid.items() if k != "total"))
    joint = {"total": float(fleet["total"] + grid["total"])}
    return {"fleet": fleet, "grid": grid, "joint": joint}

