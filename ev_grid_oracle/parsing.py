from __future__ import annotations

import re
from typing import Optional, Tuple

from .models import ActionType, ChargeRate, EVGridAction, SimulationPrediction, SimTopStation


ACTION_RE = re.compile(
    r"ACTION:\s*(?P<action>route|defer|load_shift)\s*\n"
    r"STATION:\s*(?P<station>BLR-\d\d|NONE)\s*\n"
    r"CHARGE_RATE:\s*(?P<rate>slow|fast|ultra_fast)\s*\n"
    r"DEFER_MINUTES:\s*(?P<defer>\d+)\s*\n",
    re.IGNORECASE,
)

SIM_RE = re.compile(
    r"<SIMULATE>\s*\n"
    r"T\+5_GRID_LOAD_PCT:\s*(?P<grid>[01](?:\.\d+)?)\s*\n"
    r"T\+5_RENEWABLE_PCT:\s*(?P<ren>[01](?:\.\d+)?)\s*\n"
    r"T\+5_TOP_STATIONS:\s*(?P<tops>.+?)\s*\n"
    r"</SIMULATE>",
    re.IGNORECASE | re.DOTALL,
)


def parse_simulation(text: str) -> Optional[SimulationPrediction]:
    m = SIM_RE.search(text)
    if not m:
        return None

    try:
        grid = float(m.group("grid"))
        ren = float(m.group("ren"))
        tops_raw = m.group("tops").strip()
        # Format: BLR-01:0.82:3 | BLR-11:0.77:2 | BLR-04:0.70:1
        parts = [p.strip() for p in tops_raw.split("|") if p.strip()]
        tops: list[SimTopStation] = []
        for p in parts[:3]:
            sid, load_s, q_s = [x.strip() for x in p.split(":")]
            tops.append(SimTopStation(station_id=sid.upper(), load_pct=float(load_s), queue=int(q_s)))
        if not tops:
            return None
        return SimulationPrediction(t5_grid_load_pct=grid, t5_renewable_pct=ren, t5_top_stations=tops)
    except Exception:
        return None


def parse_action(text: str, *, ev_id: str) -> Optional[EVGridAction]:
    m = ACTION_RE.search(text.strip())
    if not m:
        return None

    action_type = ActionType(m.group("action").lower())
    station = m.group("station").upper()
    rate = ChargeRate(m.group("rate").lower())
    defer = int(m.group("defer"))

    station_id = None if station == "NONE" else station

    try:
        return EVGridAction(
            action_type=action_type,
            ev_id=ev_id,
            station_id=station_id,
            charge_rate=rate,
            defer_minutes=defer,
        )
    except Exception:
        return None


def parse_simulation_and_action(text: str, *, ev_id: str) -> Tuple[Optional[SimulationPrediction], Optional[EVGridAction]]:
    """
    Parse both dream prediction and action (either can be missing).
    """
    sim = parse_simulation(text)
    act = parse_action(text, ev_id=ev_id)
    return sim, act

