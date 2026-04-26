from __future__ import annotations

from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

from ev_grid_oracle.road_env import RoadCore
from ev_grid_oracle.road_models import RoadAction, RoadObservation


class EVGridRoadEnvironment(Environment):
    """
    Separate OpenEnv environment that forces real-road-graph actions.
    Mounted as a sub-app under /road/ so it doesn't break the existing env.
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = False

    def __init__(self):
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self._core = RoadCore(g=None, nodes=[])  # type: ignore[arg-type]

    def reset(self, seed=None, episode_id=None, **kwargs) -> RoadObservation:  # type: ignore[override]
        self._state = State(episode_id=episode_id or str(uuid4()), step_count=0)
        return self._core.reset(seed=seed)

    def step(self, action: RoadAction) -> RoadObservation:  # type: ignore[override]
        self._state.step_count += 1
        return self._core.step(action)

    @property
    def state(self) -> State:
        return self._state

