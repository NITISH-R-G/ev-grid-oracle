from __future__ import annotations

import random
from dataclasses import dataclass

import networkx as nx

from ev_grid_oracle.city_graph import STATIONS
from server.road_router import get_router, haversine_m

from .road_models import RoadAction, RoadObservation, RoadState


@dataclass
class RoadCore:
    g: nx.Graph
    nodes: list[tuple[float, float]]  # (lat,lng)
    node: int = 0
    battery_pct: float = 80.0
    target_station_id: str = "BLR-11"
    steps_remaining: int = 220

    def reset(self, *, seed: int | None = None) -> RoadObservation:
        rng = random.Random(seed)
        router = get_router()
        self.g = router.g
        self.nodes = router.nodes

        # Start near MG Road; target a random station.
        start_lat, start_lng = 12.9757, 77.6070
        self.node = router.nearest_node(lat=start_lat, lng=start_lng)
        self.battery_pct = float(rng.uniform(55, 92))
        self.target_station_id = rng.choice([s.station_id for s in STATIONS])
        self.steps_remaining = 220
        return self._obs(prompt="Choose the next connected road node toward the target station.")

    def step(self, action: RoadAction) -> RoadObservation:
        flags: list[str] = []
        details: dict[str, str] = {}
        rb: dict[str, float] = {}

        if action.current_node != self.node:
            flags.append("invalid_current_node")
            details["invalid_current_node"] = f"expected {self.node} got {action.current_node}"
            return self._obs(
                prompt="Invalid action: current_node mismatch.",
                done=True,
                reward_breakdown={"total": -1.0},
                anti_cheat_flags=flags,
                anti_cheat_details=details,
            )

        if not self.g.has_edge(action.current_node, action.next_node):
            flags.append("teleportation")
            details["teleportation"] = "next_node is not a connected neighbor"
            return self._obs(
                prompt="Invalid action: next_node must be a connected neighbor.",
                done=True,
                reward_breakdown={"total": -1.0},
                anti_cheat_flags=flags,
                anti_cheat_details=details,
            )

        w_s = float(self.g.edges[action.current_node, action.next_node].get("weight", 5.0))
        self.node = int(action.next_node)
        self.steps_remaining = max(0, self.steps_remaining - 1)

        # Battery: 0.18% per minute baseline drain (tunable)
        self.battery_pct = max(0.0, self.battery_pct - (w_s / 60.0) * 0.18)

        dist_pen = -w_s / 60.0
        rb["time_min"] = dist_pen

        # Done when close to target station.
        tgt = next((s for s in STATIONS if s.station_id == self.target_station_id), STATIONS[0])
        lat, lng = self.nodes[self.node]
        d_m = haversine_m(lat, lng, tgt.lat, tgt.lng)
        rb["target_dist_km"] = -float(d_m / 1000.0) * 0.02

        done = d_m < 120.0 or self.steps_remaining <= 0 or self.battery_pct <= 0.5
        if d_m < 120.0:
            rb["arrive_bonus"] = 1.0
        if self.battery_pct <= 0.5:
            rb["battery_empty"] = -1.0

        total = float(sum(rb.values()))
        rb["total"] = total
        prompt = "Pick next_node among connected neighbors. Minimize time and distance to target."
        return self._obs(prompt=prompt, done=done, reward_breakdown=rb, anti_cheat_flags=flags, anti_cheat_details=details)

    def _obs(
        self,
        *,
        prompt: str,
        done: bool = False,
        reward_breakdown: dict[str, float] | None = None,
        anti_cheat_flags: list[str] | None = None,
        anti_cheat_details: dict[str, str] | None = None,
    ) -> RoadObservation:
        tgt = next((s for s in STATIONS if s.station_id == self.target_station_id), STATIONS[0])
        lat, lng = self.nodes[self.node]
        st = RoadState(
            node=int(self.node),
            lat=float(lat),
            lng=float(lng),
            battery_pct_0_100=float(self.battery_pct),
            target_station_id=str(self.target_station_id),
            target_lat=float(tgt.lat),
            target_lng=float(tgt.lng),
            steps_remaining=int(self.steps_remaining),
        )
        return RoadObservation(
            prompt=prompt,
            state=st,
            done=bool(done),
            reward_breakdown=reward_breakdown or {},
            anti_cheat_flags=anti_cheat_flags or [],
            anti_cheat_details=anti_cheat_details or {},
        )

