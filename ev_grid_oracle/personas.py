from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Literal


FleetPersona = Literal["TaxiFleet", "CorporateShuttle", "DeliveryFleet", "PrivateOwner", "Emergency"]
FleetMode = Literal["mixed", "taxi", "corporate", "delivery", "private", "emergency"]


@dataclass(frozen=True, slots=True)
class PersonaParams:
    persona: FleetPersona
    urgency_bias: float  # added to sampled urgency, then clamped
    max_wait_choices: tuple[int, ...]
    battery_min: float
    battery_max: float
    price_sensitivity: float  # 0..1, informational for prompt/reward later


PERSONAS: dict[FleetPersona, PersonaParams] = {
    "TaxiFleet": PersonaParams(
        persona="TaxiFleet",
        urgency_bias=0.25,
        max_wait_choices=(10, 15, 20, 30),
        battery_min=8.0,
        battery_max=70.0,
        price_sensitivity=0.75,
    ),
    "CorporateShuttle": PersonaParams(
        persona="CorporateShuttle",
        urgency_bias=0.05,
        max_wait_choices=(20, 30, 45, 60),
        battery_min=25.0,
        battery_max=85.0,
        price_sensitivity=0.35,
    ),
    "DeliveryFleet": PersonaParams(
        persona="DeliveryFleet",
        urgency_bias=0.18,
        max_wait_choices=(15, 20, 30, 45),
        battery_min=10.0,
        battery_max=75.0,
        price_sensitivity=0.55,
    ),
    "PrivateOwner": PersonaParams(
        persona="PrivateOwner",
        urgency_bias=-0.05,
        max_wait_choices=(30, 45, 60, 75),
        battery_min=30.0,
        battery_max=95.0,
        price_sensitivity=0.25,
    ),
    "Emergency": PersonaParams(
        persona="Emergency",
        urgency_bias=0.55,
        max_wait_choices=(5, 10, 15),
        battery_min=5.0,
        battery_max=55.0,
        price_sensitivity=0.10,
    ),
}


def choose_persona(rng: Random, mode: FleetMode) -> PersonaParams:
    if mode == "taxi":
        return PERSONAS["TaxiFleet"]
    if mode == "corporate":
        return PERSONAS["CorporateShuttle"]
    if mode == "delivery":
        return PERSONAS["DeliveryFleet"]
    if mode == "private":
        return PERSONAS["PrivateOwner"]
    if mode == "emergency":
        return PERSONAS["Emergency"]

    # mixed: slightly favor taxi/delivery for more drama
    r = rng.random()
    if r < 0.30:
        return PERSONAS["TaxiFleet"]
    if r < 0.52:
        return PERSONAS["DeliveryFleet"]
    if r < 0.72:
        return PERSONAS["CorporateShuttle"]
    if r < 0.92:
        return PERSONAS["PrivateOwner"]
    return PERSONAS["Emergency"]

