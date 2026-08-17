#!/bin/bash
uv run ruff check --unsafe-fixes --fix .
uv run ruff format .
