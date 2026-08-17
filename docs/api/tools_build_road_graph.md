# Documentation for ./tools/build_road_graph.py

### encode_polyline_latlng

Google polyline encoding for [lat,lng] points.
Stored as a compact ASCII string to shrink graph artifacts.

### build_adjacency

Pass 1: build point adjacency over snapped coordinates.
Intersections/endpoints are nodes where degree != 2.

### contract_edges

Pass 2: for each way, contract degree-2 chains into intersection-to-intersection edges.

### filter_largest_component

Pass 3: Keep only the largest connected component (by node count) to satisfy routing coverage.
