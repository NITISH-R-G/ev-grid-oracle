from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ChargerType:
    fast = "fast"
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

    charger_type: str
    total_slots: int = Field(..., ge=1)

    occupied_slots: int = Field(0, ge=0)
    queue_length: int = Field(0, ge=0)
    price_per_kwh: float = Field(0.0, ge=0.0)
    avg_wait_minutes: float = Field(0.0, ge=0.0)

s = StationState(station_id="1", neighborhood_slug="2", neighborhood_name="3", lat=1.0, lng=1.0, charger_type="fast", total_slots="10", occupied_slots="1")
print(type(s.occupied_slots))
print(s.occupied_slots)
