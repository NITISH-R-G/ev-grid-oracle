from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from openenv.core.env_server.types import Action, Observation

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ChargerType(str, Enum):
    slow = "slow"
    fast = "fast"
    ultra_fast = "ultra_fast"


class ChargeRate(str, Enum):
    slow = "slow"
    fast = "fast"
    ultra_fast = "ultra_fast"


class ActionType(str, Enum):
    route = "route"
    defer = "defer"
    load_shift = "load_shift"


class DayType(str, Enum):
    weekday = "weekday"
    weekend = "weekend"


class PeakRisk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class StationState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    station_id: str = Field(..., description="Stable id like BLR-01")
    neighborhood_slug: str = Field(..., description="Canonical slug like 'koramangala'")
    neighborhood_name: str = Field(..., description="Display name like 'Koramangala'")
    lat: float
    lng: float

    charger_type: ChargerType
    total_slots: int = Field(..., ge=1)

    occupied_slots: int = Field(0, ge=0)
    queue_length: int = Field(0, ge=0)
    price_per_kwh: float = Field(0.0, ge=0.0)
    avg_wait_minutes: float = Field(0.0, ge=0.0)

    @field_validator("occupied_slots")
    @classmethod
    def _occupied_le_total(cls, v: int, info):  # type: ignore[override]
        total = info.data.get("total_slots")
        if total is not None and v > total:
            raise ValueError("occupied_slots cannot exceed total_slots")
        return v


class EVRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ev_id: str
    battery_pct_0_100: float = Field(..., ge=0.0, le=100.0)
    urgency: float = Field(..., ge=0.0, le=1.0)
    neighborhood_slug: str
    neighborhood_name: str
    target_charge_pct_0_100: float = Field(..., ge=0.0, le=100.0)
    max_wait_minutes: int = Field(..., ge=0)


class BESCOMFeederState(BaseModel):
    """
    Lightweight, judge-friendly feeder snapshot (mocked but deterministic).
    """

    model_config = ConfigDict(extra="forbid")

    feeder_id: str
    zone: str
    load_pct: float = Field(..., ge=0.0, le=1.0)
    limit_pct: float = Field(..., ge=0.0, le=1.0)


class GridState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stations: list[StationState]
    pending_evs: list[EVRequest]
    grid_load_pct: float = Field(..., ge=0.0, le=1.0)
    renewable_pct: float = Field(..., ge=0.0, le=1.0)
    hour: int = Field(..., ge=0, le=23)
    minute_of_day: int = Field(0, ge=0, le=24 * 60 - 1)
    day_type: DayType
    peak_risk: PeakRisk
    bescom_feeders: list[BESCOMFeederState] = Field(default_factory=list, max_length=12)


class EVGridAction(Action):
    model_config = ConfigDict(extra="forbid")

    action_type: ActionType
    ev_id: str
    station_id: Optional[str] = None
    charge_rate: ChargeRate = ChargeRate.fast
    defer_minutes: int = Field(0, ge=0)

    @model_validator(mode="after")
    def _check_consistency(self) -> "EVGridAction":
        if self.action_type == ActionType.route:
            if not self.station_id:
                raise ValueError("station_id required when action_type='route'")
            if self.defer_minutes != 0:
                raise ValueError("defer_minutes must be 0 when action_type='route'")
        if self.action_type == ActionType.defer:
            if self.defer_minutes <= 0:
                raise ValueError("defer_minutes must be > 0 when action_type='defer'")
        if self.action_type == ActionType.load_shift:
            # For v1: still tie action to an EV (ev_id) but station optional.
            if self.defer_minutes != 0:
                raise ValueError("defer_minutes must be 0 when action_type='load_shift'")
        return self


class EVGridObservation(Observation):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    state: GridState
    done: bool = False
    reward_breakdown: dict[str, float] = Field(default_factory=dict)
    anti_cheat_flags: list[str] = Field(default_factory=list)
    anti_cheat_details: dict[str, str] = Field(default_factory=dict)


Role = Literal["fleet", "grid"]


class NegotiationMessage(BaseModel):
    """
    A short, bounded message used in the explicit multi-agent protocol.

    This is *not* a free-form chat reward. It exists so judges can see
    negotiation/constraints explicitly and we can penalize empty spam.
    """

    model_config = ConfigDict(extra="forbid")

    role: Role
    text: str = Field(..., min_length=1, max_length=320)


class GridDirective(BaseModel):
    """
    GridOperator -> FleetDispatcher constraint signal (verifiable).
    """

    model_config = ConfigDict(extra="forbid")

    max_grid_load_pct: float = Field(0.88, ge=0.0, le=1.0)
    station_blacklist: list[str] = Field(default_factory=list, max_length=10)
    price_mult: float = Field(1.0, ge=0.5, le=3.0)


class MultiAgentStepRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    seed: int | None = Field(None, ge=0, le=1_000_000)
    scenario: str | None = None

    grid_directive: GridDirective
    grid_message: NegotiationMessage | None = None

    fleet_action: EVGridAction
    fleet_message: NegotiationMessage | None = None


class MultiAgentStepResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    obs: dict[str, Any]
    tick: int
    scenario: str

    grid_directive: dict[str, Any]
    fleet_action: dict[str, Any]
    resolved_action: dict[str, Any]
    violations: list[str]
    messages: list[dict[str, Any]]


class SimTopStation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    station_id: str
    load_pct: float = Field(..., ge=0.0, le=1.0)
    queue: int = Field(..., ge=0)


class SimulationPrediction(BaseModel):
    """
    Aggregated 'dream state' prediction for T+5 ticks.
    Kept intentionally small and verifiable for hackathon judging.
    """

    model_config = ConfigDict(extra="forbid")

    t5_grid_load_pct: float = Field(..., ge=0.0, le=1.0)
    t5_renewable_pct: float = Field(..., ge=0.0, le=1.0)
    t5_top_stations: list[SimTopStation] = Field(..., min_length=1, max_length=3)


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, list):
        return [to_jsonable(x) for x in obj]
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    return obj

