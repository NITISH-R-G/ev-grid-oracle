from __future__ import annotations

import json
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Iterable, Optional

import networkx as nx


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000.0
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return r * c


def decode_polyline_latlng(s: str, *, precision: int = 5) -> list[list[float]]:
    if not s:
        return []
    factor = 10**precision
    idx = 0
    lat = 0
    lng = 0
    out: list[list[float]] = []

    def _next() -> int:
        nonlocal idx
        shift = 0
        result = 0
        while True:
            b = ord(s[idx]) - 63
            idx += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        d = ~(result >> 1) if (result & 1) else (result >> 1)
        return int(d)

    while idx < len(s):
        lat += _next()
        lng += _next()
        out.append([lat / factor, lng / factor])
    return out


@dataclass(frozen=True)
class RoadRouter:
    g: nx.Graph
    nodes: list[tuple[float, float]]  # (lat,lng) by node id
    edge_geom: dict[tuple[int, int], list[list[float]]]

    @classmethod
    def load(cls, path: Path) -> "RoadRouter":
        obj = json.loads(path.read_text(encoding="utf-8"))
        nodes_in = obj.get("nodes", [])
        edges_in = obj.get("edges", [])
        if not isinstance(nodes_in, list) or not isinstance(edges_in, list):
            raise ValueError("invalid road graph json")

        nodes: list[tuple[float, float]] = []
        for n in nodes_in:
            nodes.append((float(n["lat"]), float(n["lng"])))

        g = nx.Graph()
        for i, (lat, lng) in enumerate(nodes):
            g.add_node(i, lat=lat, lng=lng)
        edge_geom: dict[tuple[int, int], list[list[float]]] = {}
        for e in edges_in:
            a = int(e["a"])
            b = int(e["b"])
            w = float(e.get("travel_s") or 0.0)
            geom_poly = e.get("geom_poly")
            if a == b:
                continue
            # keep smallest weight if duplicates
            if g.has_edge(a, b):
                if w < float(g.edges[a, b].get("weight", 1e18)):
                    g.edges[a, b]["weight"] = w
            else:
                g.add_edge(a, b, weight=w)
            if isinstance(geom_poly, str) and geom_poly:
                precision = int(obj.get("meta", {}).get("snap_decimals", 5) or 5)
                geom = decode_polyline_latlng(geom_poly, precision=precision)
                if len(geom) >= 2:
                    edge_geom[(a, b)] = geom
                    edge_geom[(b, a)] = list(reversed(geom))

        return cls(g=g, nodes=nodes, edge_geom=edge_geom)

    def nearest_node(self, *, lat: float, lng: float) -> int:
        best = 0
        best_d = 1e18
        for i, (la, lo) in enumerate(self.nodes):
            d = haversine_m(lat, lng, la, lo)
            if d < best_d:
                best_d = d
                best = i
        return best

    def route_polyline(self, *, src_lat: float, src_lng: float, dst_lat: float, dst_lng: float) -> Optional[list[list[float]]]:
        a = self.nearest_node(lat=src_lat, lng=src_lng)
        b = self.nearest_node(lat=dst_lat, lng=dst_lng)
        try:
            path = nx.shortest_path(self.g, a, b, weight="weight")  # type: ignore[arg-type]
        except Exception:
            return None
        poly: list[list[float]] = []
        for u, v in zip(path, path[1:]):
            seg = self.edge_geom.get((int(u), int(v)))
            if seg and len(seg) >= 2:
                if poly:
                    poly.extend(seg[1:])
                else:
                    poly.extend(seg)
            else:
                # fallback: straight segment
                if not poly:
                    poly.append([self.nodes[int(u)][0], self.nodes[int(u)][1]])
                poly.append([self.nodes[int(v)][0], self.nodes[int(v)][1]])
        return poly


_ROUTER: RoadRouter | None = None


def get_router() -> RoadRouter:
    global _ROUTER
    if _ROUTER is not None:
        return _ROUTER
    root = Path(__file__).resolve().parents[1]
    p = root / "web" / "public" / "maps" / "bangalore_roads_graph.json"
    _ROUTER = RoadRouter.load(p)
    return _ROUTER

