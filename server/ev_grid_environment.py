from __future__ import annotations

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from ev_grid_oracle.city_graph import build_city_graph
from ev_grid_oracle.env import EVGridCore
from ev_grid_oracle.models import EVGridAction, EVGridObservation


class EVGridEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS: bool = False

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._core = EVGridCore(city_graph=build_city_graph())

    def reset(self, seed=None, episode_id=None, **kwargs) -> EVGridObservation:  # type: ignore[override]
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)
        obs = self._core.reset(seed=seed)
        return obs

    def step(self, action: EVGridAction) -> EVGridObservation:  # type: ignore[override]
        self._state.step_count += 1
        obs = self._core.step(action)
        return obs

    @property
    def state(self) -> State:
        return self._state

