# Documentation for `./tools/build_road_graph.py`

## Classes

### `Node`
*No docstring available.*

## Functions

### `haversine_m`
*No docstring available.*

### `_encode_signed`
*No docstring available.*

### `encode_polyline_latlng`
Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

### `speed_kmh`
*No docstring available.*

### `snap`
*No docstring available.*

### `_coords_latlng_from_geojson_line`
*No docstring available.*

### `parse_args`
*No docstring available.*

### `build_adjacency`
Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

### `contract_edges`
Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

### `filter_largest_component`
Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.

### `main`
*No docstring available.*

### `add_neighbor`
*No docstring available.*

### `get_node`
*No docstring available.*

### `flush`
*No docstring available.*
