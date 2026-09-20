# Module: `./tools/build_road_graph.py`

**Description:**
*No module docstring provided.*

## Function: `haversine_m`
*No function docstring provided.*

## Function: `_encode_signed`
*No function docstring provided.*

## Function: `encode_polyline_latlng`
Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

## Function: `speed_kmh`
*No function docstring provided.*

## Class: `Node`
*No class docstring provided.*

## Function: `snap`
*No function docstring provided.*

## Function: `_coords_latlng_from_geojson_line`
*No function docstring provided.*

## Function: `parse_args`
*No function docstring provided.*

## Function: `build_adjacency`
Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

## Function: `contract_edges`
Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

## Function: `filter_largest_component`
Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.

## Function: `main`
*No function docstring provided.*

