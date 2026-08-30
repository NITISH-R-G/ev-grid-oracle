# Documentation for `tools/build_road_graph.py`

## Classes

### Class `Node`

No documentation provided.

## Functions

### Function `haversine_m`

No documentation provided.

### Function `_encode_signed`

No documentation provided.

### Function `encode_polyline_latlng`

Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

### Function `speed_kmh`

No documentation provided.

### Function `snap`

No documentation provided.

### Function `_coords_latlng_from_geojson_line`

No documentation provided.

### Function `parse_args`

No documentation provided.

### Function `build_adjacency`

Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

### Function `contract_edges`

Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

### Function `filter_largest_component`

Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.

### Function `main`

No documentation provided.

### Function `add_neighbor`

No documentation provided.

### Function `get_node`

No documentation provided.

### Function `flush`

No documentation provided.
