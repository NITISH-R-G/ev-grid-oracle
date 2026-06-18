# Contributing

Thank you for investing your time in contributing to our project!

Read our [Code of Conduct](./CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## Quick Start

1. Ensure you have `uv` and Node.js 22+ installed.
2. Clone the repository and install Python dependencies: `uv sync --all-extras`
3. Install frontend dependencies: `cd web && npm ci`
4. Run validation checks before committing: `./validate-submission.sh`

## Code Style

- We use Ruff for Python formatting and linting.
- We use Prettier for frontend formatting.
- PRs must pass `mypy` and `pytest` checks.
