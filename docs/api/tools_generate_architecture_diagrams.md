# API Documentation for `tools/generate_architecture_diagrams.py`

## Module Description
Autonomous Architecture Graph Generator.
Parses Python files using the `ast` module to build a dependency graph
of imports, and outputs it to `artifacts/architecture_graph.json`.

## Function `build_architecture_graph`
