from __future__ import annotations

from typing import Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, ConfigDict, Field, model_validator


class RoadAction(Action):
    """
    Minimal action space for RL on a real road graph:
    choose the next connected node (no teleportation).
    """

    model_config = ConfigDict(extra="forbid")

    current_node: int = Field(..., ge=0)
    next_node: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _non_trivial(self) -> "RoadAction":
        if self.current_node == self.next_node:
            raise ValueError("next_node must differ from current_node")
        return self


class RoadState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node: int = Field(..., ge=0)
    lat: float
    lng: float
    battery_pct_0_100: float = Field(..., ge=0.0, le=100.0)
    target_station_id: str
    target_lat: float
    target_lng: float
    steps_remaining: int = Field(..., ge=0)


class RoadObservation(Observation):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    state: RoadState
    done: bool = False
    reward_breakdown: dict[str, float] = Field(default_factory=dict)
    anti_cheat_flags: list[str] = Field(default_factory=list)
    anti_cheat_details: dict[str, str] = Field(default_factory=dict)

