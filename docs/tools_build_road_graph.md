# Documentation for tools/build_road_graph.py

## Classes

### Node
No docstring provided.

## Functions

### haversine_m
No docstring provided.

### _encode_signed
No docstring provided.

### encode_polyline_latlng
Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

### speed_kmh
No docstring provided.

### snap
No docstring provided.

### _coords_latlng_from_geojson_line
No docstring provided.

### parse_args
No docstring provided.

### build_adjacency
Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

### contract_edges
Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

### filter_largest_component
Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.

### main
No docstring provided.

### add_neighbor
No docstring provided.

### get_node
No docstring provided.

### flush
No docstring provided.
