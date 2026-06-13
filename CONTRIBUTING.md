# Contributing Guidelines

Thank you for investing your time in contributing to our project!

## Development Setup

1. Clone the repository.
2. Ensure you have `uv` installed (`pip install uv`).
3. Set up the environment: `uv sync --all-extras` or `uv pip install -e ".[dev,demo]"`
4. Set up the frontend: `cd web && npm install`

## Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes (`uv run pytest tests/`).
5. Ensure code is formatted correctly (`uv run ruff check --fix .` and `uv run ruff format .`).
6. Ensure frontend is tested and formatted (`npm test`, `npx prettier --write .`).
7. Execute `./validate-submission.sh` before submitting.

## Reporting Bugs

Please use the provided issue templates to report bugs. Include a minimal reproducible example if possible.
