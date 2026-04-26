from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypedDict


ScenarioName = Literal[
    "baseline",
    "heatwave_peak",
    "festival_surge",
    "transformer_derate",
    "station_outage",
    "tariff_shock",
    "MonsoonStorm",
    "CricketFinal",
    "AirportRush",
    "SilkBoardJam",
    "WhitefieldNight",
]


class ScenarioEvent(TypedDict, total=False):
    id: str
    tick: int
    type: str
    meta: dict[str, Any]


@dataclass
class ScenarioModifiers:
    """
    Lightweight knobs applied on top of the core simulator.
    These are intentionally simple and deterministic for replayable judging.
    """

    # Additive delta applied to computed grid_load_pct, clamped to [0, 1].
    grid_load_delta: float = 0.0

    # Multiplier on sampled arrivals per step.
    arrivals_mult: float = 1.0

    # Multiplier on station price_per_kwh (used for storytelling/UI; reward can incorporate later).
    price_mult: float = 1.0

    # Baseline prices captured at reset (so we don't compound multipliers every tick).
    base_prices: dict[str, float] | None = None

    # If set, reduces total_slots for a given station_id (simulates outage/derate).
    slot_derate: dict[str, int] | None = None


def scenario_schedule(name: ScenarioName) -> list[ScenarioEvent]:
    """
    Deterministic, fixed-tick stress tests (OpenOfficeRL-style).

    Note: ticks are env steps (5-minute increments by default).
    """
    if name == "baseline":
        return []

    if name == "heatwave_peak":
        # Gradually rising base load, then a pronounced evening spike.
        return [
            {"tick": 6, "type": "heatwave_start", "meta": {"grid_load_delta": 0.04}},
            {"tick": 18, "type": "heatwave_ramp", "meta": {"grid_load_delta": 0.08}},
            {"tick": 30, "type": "heatwave_peak", "meta": {"grid_load_delta": 0.14}},
        ]

    if name == "festival_surge":
        # Demand surge + queues explode unless dispatch adapts.
        return [
            {"tick": 8, "type": "festival_surge", "meta": {"arrivals_mult": 1.6}},
            {"tick": 26, "type": "festival_second_wave", "meta": {"arrivals_mult": 2.0}},
        ]

    if name == "transformer_derate":
        # Grid is more fragile: effective headroom drops.
        return [
            {"tick": 10, "type": "transformer_derate", "meta": {"grid_load_delta": 0.10}},
            {"tick": 28, "type": "derate_worsens", "meta": {"grid_load_delta": 0.16}},
        ]

    if name == "station_outage":
        # One major station loses capacity mid-episode.
        return [
            {"tick": 14, "type": "station_outage", "meta": {"station_id": "BLR-07", "new_total_slots": 1}},
            {"tick": 22, "type": "spillover", "meta": {"arrivals_mult": 1.3}},
        ]

    if name == "tariff_shock":
        # Tariff spike nudges policy to load shift / avoid expensive stations.
        return [
            {"tick": 12, "type": "tariff_shock", "meta": {"price_mult": 1.35}},
            {"tick": 24, "type": "tariff_shock_2", "meta": {"price_mult": 1.55}},
        ]

    if name == "MonsoonStorm":
        # Solar drops + random outages + demand surge (city floods).
        return [
            {"tick": 6, "type": "monsoon_start", "meta": {"grid_load_delta": 0.06, "arrivals_mult": 1.35}},
            {"tick": 14, "type": "station_outage", "meta": {"station_id": "BLR-14", "new_total_slots": 2}},
            {"tick": 22, "type": "station_outage", "meta": {"station_id": "BLR-07", "new_total_slots": 1}},
            {"tick": 28, "type": "monsoon_worst", "meta": {"grid_load_delta": 0.14, "arrivals_mult": 1.6}},
        ]

    if name == "CricketFinal":
        # Evening mega-spike and queues explode unless fleet adapts.
        return [
            {"tick": 10, "type": "pre_game", "meta": {"arrivals_mult": 1.4}},
            {"tick": 18, "type": "stadium_peak", "meta": {"arrivals_mult": 2.2, "grid_load_delta": 0.08}},
            {"tick": 26, "type": "post_game_exit", "meta": {"arrivals_mult": 2.5, "grid_load_delta": 0.12}},
        ]

    if name == "AirportRush":
        # Sustained demand + price spike (taxis), plus grid headroom tightens.
        return [
            {"tick": 8, "type": "airport_rush", "meta": {"arrivals_mult": 1.7}},
            {"tick": 16, "type": "tariff_shock", "meta": {"price_mult": 1.45}},
            {"tick": 24, "type": "transformer_derate", "meta": {"grid_load_delta": 0.12}},
        ]

    if name == "SilkBoardJam":
        # Congestion-like effect simulated via increased arrivals + localized outage.
        return [
            {"tick": 6, "type": "jam_start", "meta": {"arrivals_mult": 1.5}},
            {"tick": 12, "type": "station_outage", "meta": {"station_id": "BLR-11", "new_total_slots": 2}},
            {"tick": 20, "type": "spillover", "meta": {"arrivals_mult": 1.8}},
        ]

    if name == "WhitefieldNight":
        # Late-night shift: lower renewables, high commercial load, tariff pressure.
        return [
            {"tick": 10, "type": "night_commercial", "meta": {"grid_load_delta": 0.10}},
            {"tick": 18, "type": "tariff_shock", "meta": {"price_mult": 1.50}},
            {"tick": 26, "type": "night_second_wave", "meta": {"arrivals_mult": 1.6}},
        ]

    # Exhaustive check
    raise ValueError(f"Unknown scenario: {name}")


# Judge-friendly deterministic story seeds (replayable).
STORY_SEEDS: dict[str, int] = {
    "MonsoonStorm": 1107,
    "CricketFinal": 1804,
    "AirportRush": 2409,
    "SilkBoardJam": 1212,
    "WhitefieldNight": 2217,
    "heatwave_peak": 1618,
    "festival_surge": 2026,
    "transformer_derate": 2828,
    "station_outage": 1414,
    "tariff_shock": 2424,
}


def apply_scenario_events(
    *,
    name: ScenarioName,
    tick: int,
    schedule: list[ScenarioEvent],
    modifiers: ScenarioModifiers,
) -> tuple[ScenarioModifiers, list[ScenarioEvent]]:
    """
    Returns updated modifiers and the list of events that fired this tick.
    """
    fired = [e for e in schedule if int(e["tick"]) == int(tick)]
    if not fired:
        return modifiers, []

    # Stable ids for bookmarks / UI (deterministic).
    for e in fired:
        e.setdefault("id", f"{name}:{int(e['tick'])}:{str(e.get('type',''))}")

    # Modifiers are "sticky": once an event changes a knob, it persists.
    for e in fired:
        meta = e.get("meta", {})
        if "grid_load_delta" in meta:
            modifiers.grid_load_delta = float(meta["grid_load_delta"])
        if "arrivals_mult" in meta:
            modifiers.arrivals_mult = float(meta["arrivals_mult"])
        if "price_mult" in meta:
            modifiers.price_mult = float(meta["price_mult"])
        if e.get("type") == "station_outage":
            sid = str(meta.get("station_id", ""))
            new_slots = int(meta.get("new_total_slots", 1))
            if sid:
                if modifiers.slot_derate is None:
                    modifiers.slot_derate = {}
                modifiers.slot_derate[sid] = max(1, new_slots)

    return modifiers, fired

