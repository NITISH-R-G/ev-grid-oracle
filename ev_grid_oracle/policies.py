from __future__ import annotations

from ev_grid_oracle.city_graph import travel_time_minutes
from ev_grid_oracle.models import ActionType, ChargeRate, EVGridAction, GridState


def baseline_policy(state: GridState, graph) -> EVGridAction:
    """
    Greedy baseline: pick station minimizing (travel_time + wait + stress + price), avoid full.

    Deterministic given state.
    """
    ev = state.pending_evs[0]
    ev_id = ev.ev_id

    best_station = None
    best_score = float("inf")
    for s in state.stations:
        if s.occupied_slots >= s.total_slots:
            continue

        try:
            from_station = next(x for x in state.stations if x.neighborhood_slug == ev.neighborhood_slug)
            tmin = travel_time_minutes(graph, from_station.station_id, s.station_id, default_if_missing=90.0)
        except Exception:
            tmin = 60.0

        load = s.occupied_slots / max(1, s.total_slots)
        stress = 50.0 if load > 0.85 else 0.0
        score = tmin + s.avg_wait_minutes * 1.2 + stress + s.price_per_kwh * 0.3 + s.queue_length * 2.0
        if score < best_score:
            best_score = score
            best_station = s

    if best_station is None:
        return EVGridAction(action_type=ActionType.defer, ev_id=ev_id, defer_minutes=5)

    return EVGridAction(
        action_type=ActionType.route,
        ev_id=ev_id,
        station_id=best_station.station_id,
        charge_rate=ChargeRate.fast,
        defer_minutes=0,
    )

