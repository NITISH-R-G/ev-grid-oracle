# Documentation for tools/build_road_graph.py

## Classes

### Node
## Functions

### haversine_m
### _encode_signed
### encode_polyline_latlng
```text
Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.
```

### speed_kmh
### snap
### _coords_latlng_from_geojson_line
### parse_args
### build_adjacency
```text
Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.
```

### contract_edges
```text
Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.
```

### filter_largest_component
```text
Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.
```

### main
### add_neighbor
### get_node
### flush
