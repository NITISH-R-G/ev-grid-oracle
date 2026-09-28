# Contributing

First off, thank you for considering contributing to this repository!

## Code of Conduct

By participating, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md).

## Submitting Pull Requests

1. **Fork** the repo on GitHub.
2. **Clone** the project to your own machine.
3. **Commit** changes to your own branch.
4. **Push** your work back up to your fork.
5. Submit a **Pull request** so that we can review your changes.

NOTE: Be sure to merge the latest from "upstream" before making a pull request!

## Development Setup

1. Install `uv`.
2. Run `uv pip install -e ".[dev,demo]"` to install all development dependencies.
3. Run formatting and linting using `uv run ruff check .` and `uv run ruff format .`
4. Run tests with `uv run pytest tests/`
