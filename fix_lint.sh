#!/bin/bash
uv pip install --system -e ".[dev,demo]"
ruff check --fix --unsafe-fixes .
ruff format .
