from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from typing import Optional

import networkx as nx

from .city_graph import STATIONS
from .demand_sim import sample_arrivals_per_step
from .grid_sim import update_grid_load
from .models import (
    ActionType,
    ChargeRate,
    DayType,
    EVGridAction,
    EVGridObservation,
    EVRequest,
    GridState,
    PeakRisk,
    StationState,
)
from .reward import compute_reward


@dataclass
class EVGridCore:
    """
    Core env logic (no HTTP). Server wraps this.

    v0 slice: deterministic schema, minimal dynamics.
    Next slices add demand_sim/grid_sim/reward engine.
    """

    city_graph: nx.Graph
    step_count: int = 0
    max_steps: int = 48
    step_minutes: int = 5
    rng: Random = field(default_factory=Random)
    _grid_state: Optional[GridState] = None

    def reset(self, *, seed: Optional[int] = None) -> EVGridObservation:
        if seed is not None:
            self.rng.seed(seed)
        self.step_count = 0

        hour = self.rng.randint(0, 23)
        day_type = self.rng.choice([DayType.weekday, DayType.weekend])

        stations = [
            StationState(
                station_id=s.station_id,
                neighborhood_slug=s.neighborhood_slug,
                neighborhood_name=s.neighborhood_name,
                lat=s.lat,
                lng=s.lng,
                charger_type=s.charger_type,
                total_slots=s.total_slots,
                occupied_slots=self.rng.randint(0, max(0, s.total_slots - 1)),
                queue_length=self.rng.randint(0, 5),
                price_per_kwh=round(self.rng.uniform(12.0, 24.0), 2),
                avg_wait_minutes=0.0,
            )
            for s in STATIONS
        ]

        pending = [_make_ev(self.rng, i, stations) for i in range(self.rng.randint(3, 8))]

        occupied_total = sum(s.occupied_slots for s in stations)
        grid_load, renewable = update_grid_load(
            hour=hour,
            day_type=day_type.value,
            occupied_slots_total=occupied_total,
            load_shift_action_strength=0.0,
        )
        peak_risk = _peak_risk(grid_load)

        self._grid_state = GridState(
            stations=stations,
            pending_evs=pending,
            grid_load_pct=grid_load,
            renewable_pct=renewable,
            hour=hour,
            day_type=day_type,
            peak_risk=peak_risk,
        )

        _update_station_waits(self._grid_state, step_minutes=self.step_minutes)
        prompt = _build_prompt(self._grid_state)
        return EVGridObservation(prompt=prompt, state=self._grid_state, done=False, reward_breakdown={})

    def step(self, action: EVGridAction) -> EVGridObservation:
        if self._grid_state is None:
            return self.reset()

        prev_state = self._grid_state
        self.step_count += 1

        # 1) apply action (deterministic validation + state mutation)
        action_effect = _apply_action(prev_state, action)

        # 2) advance sim 5 minutes
        prev_state.hour = (prev_state.hour + (self.step_minutes // 60)) % 24  # stays same for 5-min steps
        _drain_queues_and_charging(prev_state)

        # 3) new arrivals
        arrivals = sample_arrivals_per_step(self.rng, prev_state.hour, day_type=prev_state.day_type.value)
        for _ in range(arrivals):
            prev_state.pending_evs.append(_make_ev(self.rng, self.rng.randint(1000, 9999), prev_state.stations))

        # cap pending list for prompt/training cost (env still realistic enough)
        if len(prev_state.pending_evs) > 5:
            prev_state.pending_evs = prev_state.pending_evs[:5]

        # 4) grid update + peak risk
        occupied_total = sum(s.occupied_slots for s in prev_state.stations)
        load_shift_strength = 0.03 if action.action_type == ActionType.load_shift else 0.0
        grid_load, renewable = update_grid_load(
            hour=prev_state.hour,
            day_type=prev_state.day_type.value,
            occupied_slots_total=occupied_total,
            load_shift_action_strength=load_shift_strength,
        )
        prev_state.grid_load_pct = grid_load
        prev_state.renewable_pct = renewable
        prev_state.peak_risk = _peak_risk(grid_load)

        # 5) wait estimates + reward
        _update_station_waits(prev_state, step_minutes=self.step_minutes)
        total_reward, reward_breakdown = compute_reward(prev_state=prev_state, action=action, next_state=prev_state)

        # merge effects into breakdown (debug)
        reward_breakdown = {**reward_breakdown, **action_effect}
        reward_breakdown["total"] = total_reward

        done = self.step_count >= self.max_steps
        prompt = _build_prompt(prev_state)
        return EVGridObservation(prompt=prompt, state=prev_state, done=done, reward_breakdown=reward_breakdown)


def _peak_risk(grid_load_pct: float) -> PeakRisk:
    if grid_load_pct >= 0.92:
        return PeakRisk.critical
    if grid_load_pct >= 0.85:
        return PeakRisk.high
    if grid_load_pct >= 0.70:
        return PeakRisk.medium
    return PeakRisk.low


def _make_ev(rng: Random, i: int, stations: list[StationState]) -> EVRequest:
    s = rng.choice(stations)
    battery = rng.uniform(5.0, 100.0)
    urgency = 1.0 if battery < 15.0 else rng.uniform(0.0, 1.0)
    return EVRequest(
        ev_id=f"EV-{i+1:03d}",
        battery_pct_0_100=round(battery, 1),
        urgency=round(urgency, 2),
        neighborhood_slug=s.neighborhood_slug,
        neighborhood_name=s.neighborhood_name,
        target_charge_pct_0_100=round(rng.uniform(max(battery, 40.0), 95.0), 1),
        max_wait_minutes=int(rng.choice([15, 20, 30, 45, 60])),
    )


def _apply_action(state: GridState, action: EVGridAction) -> dict[str, float]:
    out: dict[str, float] = {}
    if not state.pending_evs:
        out["no_pending"] = 0.0
        return out

    if action.action_type == ActionType.defer:
        out["action/defer"] = -0.05
        # keep EV in pending; nudge urgency up a bit
        for ev in state.pending_evs:
            if ev.ev_id == action.ev_id:
                ev.urgency = min(1.0, round(ev.urgency + 0.05, 2))
        return out

    if action.action_type == ActionType.load_shift:
        out["action/load_shift"] = 0.05
        return out

    # route
    station = next((s for s in state.stations if s.station_id == action.station_id), None)
    if station is None:
        out["action/invalid_station"] = -1.0
        return out

    if station.occupied_slots >= station.total_slots:
        station.queue_length += 1
        out["action/full_station"] = -0.5
        return out

    station.occupied_slots += 1
    if station.queue_length > 0:
        station.queue_length -= 1

    out["action/route"] = 0.1
    # remove EV if matches
    state.pending_evs = [ev for ev in state.pending_evs if ev.ev_id != action.ev_id]
    return out


def _drain_queues_and_charging(state: GridState) -> None:
    # deterministic service per 5-min step by charger type
    for s in state.stations:
        if s.charger_type.value == "ultra_fast":
            complete = max(1, s.total_slots // 3)
        elif s.charger_type.value == "fast":
            complete = max(1, s.total_slots // 5)
        else:
            complete = max(1, s.total_slots // 7)

        done = min(s.occupied_slots, complete)
        s.occupied_slots -= done

        # fill from queue if slots free
        free = max(0, s.total_slots - s.occupied_slots)
        take = min(free, s.queue_length)
        s.occupied_slots += take
        s.queue_length -= take


def _update_station_waits(state: GridState, *, step_minutes: int) -> None:
    # rough wait: queue * step_minutes scaled by charger speed
    for s in state.stations:
        if s.charger_type.value == "ultra_fast":
            factor = 0.6
        elif s.charger_type.value == "fast":
            factor = 1.0
        else:
            factor = 1.4
        s.avg_wait_minutes = float(round(s.queue_length * step_minutes * factor, 2))


def _build_prompt(state: GridState) -> str:
    # Keep prompt stable for GRPO parsing later.
    lines: list[str] = []
    lines.append("BANGALORE EV GRID — ROUTING DECISION REQUIRED")
    lines.append("=" * 46)
    lines.append(
        f"Time: {state.hour:02d}:00 | Day: {state.day_type.value} | Grid Load: {state.grid_load_pct*100:.1f}% | Renewable: {state.renewable_pct*100:.1f}%"
    )
    lines.append(f"Peak Risk: {state.peak_risk.value}")
    lines.append("")
    lines.append("CHARGING STATIONS:")
    lines.append("[station_id | type | load | queue | price]")
    for s in state.stations[:10]:
        load = (s.occupied_slots / max(1, s.total_slots)) * 100.0
        lines.append(
            f"{s.station_id} | {s.charger_type.value} | {load:.0f}% | {s.queue_length} | ₹{s.price_per_kwh:.2f}/kWh"
        )
    lines.append("... (15 more)")
    lines.append("")
    if state.pending_evs:
        ev = state.pending_evs[0]
        crit = " 🔴 CRITICAL" if ev.battery_pct_0_100 < 15.0 else ""
        lines.append("PENDING EV REQUEST:")
        lines.append(f"  EV #{ev.ev_id}")
        lines.append(f"  Battery: {ev.battery_pct_0_100:.1f}%{crit}")
        lines.append(f"  Location: {ev.neighborhood_name}")
        lines.append(f"  Needs: charge to {ev.target_charge_pct_0_100:.1f}%")
        lines.append(f"  Max wait: {ev.max_wait_minutes} min | Urgency: {ev.urgency:.2f}")
    else:
        lines.append("PENDING EV REQUEST:")
        lines.append("  None")
    lines.append("")
    lines.append("RESPOND IN THIS EXACT FORMAT (DREAM THEN ACT):")
    lines.append("")
    lines.append("<SIMULATE>")
    lines.append("T+5_GRID_LOAD_PCT: 0.00-1.00")
    lines.append("T+5_RENEWABLE_PCT: 0.00-1.00")
    lines.append("T+5_TOP_STATIONS: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1")
    lines.append("</SIMULATE>")
    lines.append("")
    lines.append("ACTION: route|defer|load_shift")
    lines.append("STATION: BLR-01..BLR-25 or NONE")
    lines.append("CHARGE_RATE: slow|fast|ultra_fast")
    lines.append("DEFER_MINUTES: integer")
    lines.append("REASON: [max 20 words]")
    lines.append("CONFIDENCE: [0.0-1.0]")
    return "\n".join(lines)

