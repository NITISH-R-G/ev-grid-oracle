from __future__ import annotations

from dataclasses import dataclass, field

from .models import ActionType, EVGridAction, GridState


@dataclass
class RewardHackDetector:
    """
    Stateful, deterministic detector for common reward-hacking patterns.

    Goal: give the existing anti-hack flags "teeth" by detecting multi-step
    exploit patterns, not just single-step invalidity.
    """

    # consecutive defer streak per EV
    defer_streak: dict[str, int] = field(default_factory=dict)

    # consecutive routing concentration (same station repeatedly)
    last_station_id: str | None = None
    station_streak: int = 0

    def reset(self) -> None:
        self.defer_streak.clear()
        self.last_station_id = None
        self.station_streak = 0

    def step(
        self, *, prev: GridState, action: EVGridAction, next_state: GridState
    ) -> tuple[dict[str, float], list[str], dict[str, str]]:
        rb: dict[str, float] = {}
        flags: list[str] = []
        details: dict[str, str] = {}

        def add(flag: str, detail: str, penalty: float) -> None:
            if flag not in flags:
                flags.append(flag)
            details[flag] = detail
            rb[f"anti_hack/{flag}"] = float(penalty)

        # 1) 3+ consecutive defers for the same EV (stalling exploit)
        if action.action_type == ActionType.defer:
            k = str(action.ev_id)
            self.defer_streak[k] = int(self.defer_streak.get(k, 0)) + 1
            if self.defer_streak[k] >= 3:
                add("defer_stalling", f"ev_id={k} defer_streak={self.defer_streak[k]}", penalty=-2.5)
        else:
            # reset streak when EV is acted on non-defer
            if str(action.ev_id) in self.defer_streak:
                self.defer_streak[str(action.ev_id)] = 0

        # 2) Station concentration: repeatedly routing into the same station
        if action.action_type == ActionType.route and action.station_id:
            sid = str(action.station_id)
            if self.last_station_id == sid:
                self.station_streak += 1
            else:
                self.last_station_id = sid
                self.station_streak = 1

            # If queue is growing while we keep piling onto same station, flag it.
            st_prev = next((s for s in prev.stations if s.station_id == sid), None)
            st_next = next((s for s in next_state.stations if s.station_id == sid), None)
            if st_prev and st_next:
                grew = int(st_next.queue_length) > int(st_prev.queue_length)
                if self.station_streak >= 3 and (int(st_next.queue_length) >= 6 or grew):
                    add(
                        "queue_piling_streak",
                        f"station_id={sid} streak={self.station_streak} queue={st_next.queue_length} grew={grew}",
                        penalty=-3.0,
                    )

        return rb, flags, details

