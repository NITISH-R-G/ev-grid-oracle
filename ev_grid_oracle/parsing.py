from __future__ import annotations

import re
from typing import Optional

from .models import ActionType, ChargeRate, EVGridAction


ACTION_RE = re.compile(
    r"ACTION:\s*(?P<action>route|defer|load_shift)\s*\n"
    r"STATION:\s*(?P<station>BLR-\d\d|NONE)\s*\n"
    r"CHARGE_RATE:\s*(?P<rate>slow|fast|ultra_fast)\s*\n"
    r"DEFER_MINUTES:\s*(?P<defer>\d+)\s*\n",
    re.IGNORECASE,
)


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

