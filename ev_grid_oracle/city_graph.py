from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Iterable, Optional

import networkx as nx

from .models import ChargerType


@dataclass(frozen=True, slots=True)
class StationSpec:
    station_id: str
    neighborhood_slug: str
    neighborhood_name: str
    lat: float
    lng: float
    charger_type: ChargerType
    total_slots: int


STATIONS: list[StationSpec] = [
    StationSpec("BLR-01", "koramangala", "Koramangala", 12.9352, 77.6245, ChargerType.fast, 12),
    StationSpec("BLR-02", "whitefield", "Whitefield", 12.9698, 77.7500, ChargerType.ultra_fast, 16),
    StationSpec("BLR-03", "hsr_layout", "HSR Layout", 12.9116, 77.6389, ChargerType.fast, 10),
    StationSpec("BLR-04", "indiranagar", "Indiranagar", 12.9784, 77.6408, ChargerType.fast, 12),
    StationSpec("BLR-05", "electronic_city", "Electronic City", 12.8399, 77.6770, ChargerType.slow, 14),
    StationSpec("BLR-06", "marathahalli", "Marathahalli", 12.9591, 77.7006, ChargerType.fast, 12),
    StationSpec("BLR-07", "jayanagar", "Jayanagar", 12.9308, 77.5832, ChargerType.slow, 10),
    StationSpec("BLR-08", "yeshwanthpur", "Yeshwanthpur", 13.0245, 77.5497, ChargerType.fast, 12),
    StationSpec("BLR-09", "hebbal", "Hebbal", 13.0350, 77.5970, ChargerType.ultra_fast, 12),
    StationSpec("BLR-10", "sarjapur", "Sarjapur", 12.9010, 77.6960, ChargerType.slow, 8),
    StationSpec("BLR-11", "mg_road", "MG Road", 12.9757, 77.6070, ChargerType.ultra_fast, 12),
    StationSpec("BLR-12", "bellandur", "Bellandur", 12.9258, 77.6681, ChargerType.fast, 12),
    StationSpec("BLR-13", "bannerghatta", "Bannerghatta", 12.8636, 77.5771, ChargerType.slow, 10),
    StationSpec("BLR-14", "rajajinagar", "Rajajinagar", 12.9890, 77.5522, ChargerType.fast, 12),
    StationSpec("BLR-15", "jp_nagar", "JP Nagar", 12.9063, 77.5857, ChargerType.slow, 10),
    StationSpec("BLR-16", "btm_layout", "BTM Layout", 12.9165, 77.6101, ChargerType.fast, 10),
    StationSpec("BLR-17", "cunningham_road", "Cunningham Road", 12.9897, 77.5954, ChargerType.ultra_fast, 8),
    StationSpec("BLR-18", "yelahanka", "Yelahanka", 13.1004, 77.5963, ChargerType.slow, 10),
    StationSpec("BLR-19", "kengeri", "Kengeri", 12.9140, 77.4830, ChargerType.slow, 8),
    StationSpec("BLR-20", "tumkur_road", "Tumkur Road", 13.0250, 77.5100, ChargerType.slow, 12),
    StationSpec("BLR-21", "old_airport_road", "Old Airport Road", 12.9601, 77.6477, ChargerType.fast, 10),
    StationSpec("BLR-22", "kr_puram", "KR Puram", 13.0050, 77.6950, ChargerType.fast, 10),
    StationSpec("BLR-23", "silk_board", "Silk Board", 12.9176, 77.6228, ChargerType.fast, 12),
    StationSpec("BLR-24", "cv_raman_nagar", "CV Raman Nagar", 12.9860, 77.6600, ChargerType.slow, 8),
    StationSpec("BLR-25", "domlur", "Domlur", 12.9610, 77.6390, ChargerType.fast, 10),
]


_BY_ID = {s.station_id: s for s in STATIONS}
_BY_SLUG = {s.neighborhood_slug: s for s in STATIONS}


CBD = ["mg_road", "cunningham_road", "domlur", "indiranagar", "old_airport_road", "cv_raman_nagar"]
EAST = ["whitefield", "marathahalli", "bellandur", "sarjapur", "kr_puram"]
SOUTH = [
    "koramangala",
    "hsr_layout",
    "btm_layout",
    "silk_board",
    "jp_nagar",
    "jayanagar",
    "bannerghatta",
    "electronic_city",
]
NORTH_WEST = ["hebbal", "yelahanka", "yeshwanthpur", "rajajinagar", "tumkur_road", "kengeri"]


def get_station_by_id(station_id: str) -> StationSpec:
    return _BY_ID[station_id]


def get_station_by_slug(neighborhood_slug: str) -> StationSpec:
    return _BY_SLUG[neighborhood_slug]


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def _edge_minutes(a: StationSpec, b: StationSpec, *, minutes_per_km: float = 5.0, base: float = 2.0) -> float:
    # Hackathon v1: convert geo distance -> travel minutes with a small base overhead.
    # `minutes_per_km` approximates city traffic; tweak later without changing API.
    km = haversine_km(a.lat, a.lng, b.lat, b.lng)
    return base + km * minutes_per_km


def _add_chain_edges(g: nx.Graph, slugs: Iterable[str]) -> None:
    slugs = list(slugs)
    for i in range(len(slugs) - 1):
        a = get_station_by_slug(slugs[i])
        b = get_station_by_slug(slugs[i + 1])
        g.add_edge(a.station_id, b.station_id, weight_minutes=_edge_minutes(a, b))


def _add_dense_within_cluster(g: nx.Graph, slugs: list[str]) -> None:
    # Make cluster connected + add a few extra edges for alternate routes.
    _add_chain_edges(g, slugs)
    if len(slugs) >= 3:
        for i in range(0, len(slugs) - 2, 2):
            a = get_station_by_slug(slugs[i])
            b = get_station_by_slug(slugs[i + 2])
            g.add_edge(a.station_id, b.station_id, weight_minutes=_edge_minutes(a, b))


def build_city_graph() -> nx.Graph:
    g = nx.Graph()
    for s in STATIONS:
        g.add_node(
            s.station_id,
            station_id=s.station_id,
            neighborhood_slug=s.neighborhood_slug,
            neighborhood_name=s.neighborhood_name,
            lat=s.lat,
            lng=s.lng,
            charger_type=s.charger_type.value,
            total_slots=s.total_slots,
        )

    _add_dense_within_cluster(g, CBD)
    _add_dense_within_cluster(g, EAST)
    _add_dense_within_cluster(g, SOUTH)
    _add_dense_within_cluster(g, NORTH_WEST)

    # Bridges (manual "major corridors")
    bridges = [
        ("mg_road", "indiranagar"),
        ("indiranagar", "cv_raman_nagar"),
        ("cv_raman_nagar", "marathahalli"),
        ("marathahalli", "whitefield"),
        ("domlur", "bellandur"),
        ("koramangala", "domlur"),
        ("koramangala", "mg_road"),
        ("silk_board", "bellandur"),
        ("hsr_layout", "bellandur"),
        ("hsr_layout", "sarjapur"),
        ("electronic_city", "sarjapur"),
        ("rajajinagar", "cunningham_road"),
        ("yeshwanthpur", "hebbal"),
        ("hebbal", "cunningham_road"),
        ("kengeri", "rajajinagar"),
        ("tumkur_road", "yeshwanthpur"),
    ]
    for a_slug, b_slug in bridges:
        a = get_station_by_slug(a_slug)
        b = get_station_by_slug(b_slug)
        g.add_edge(a.station_id, b.station_id, weight_minutes=_edge_minutes(a, b))

    if not nx.is_connected(g):
        # Fail fast: graph must be connected for routing to work.
        comps = [sorted(list(c)) for c in nx.connected_components(g)]
        raise RuntimeError(f"city graph not connected, components={comps}")

    return g


def travel_time_minutes(
    g: nx.Graph, from_station_id: str, to_station_id: str, *, default_if_missing: Optional[float] = None
) -> float:
    if from_station_id == to_station_id:
        return 0.0
    try:
        return float(
            nx.shortest_path_length(g, from_station_id, to_station_id, weight="weight_minutes")  # type: ignore[arg-type]
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        if default_if_missing is not None:
            return float(default_if_missing)
        raise


def nearest_stations_by_geo(lat: float, lng: float, *, k: int = 5) -> list[StationSpec]:
    ranked = sorted(STATIONS, key=lambda s: haversine_km(lat, lng, s.lat, s.lng))
    return ranked[:k]

