#!/bin/bash
mkdir -p docs/architecture
pydeps ev_grid_oracle --noshow -o docs/architecture/ev_grid_oracle_deps.svg
pydeps server --noshow -o docs/architecture/server_deps.svg
