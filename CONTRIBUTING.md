# Contributing Guidelines

Thank you for your interest in contributing! We welcome all contributions, big and small.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Set up the environment**: Run `uv pip install -e ".[dev,demo]"` to install all dependencies.
3. **Make your changes**. Ensure your code is clean and follows the existing style.
4. **Test your changes**: Run tests using `uv run pytest tests/`.
5. **Run pre-commit checks**: Run `./validate-submission.sh` via `uv` as described in the README/memory.
6. **Submit a pull request**: Open a PR against the `main` branch. Describe your changes in detail.

## Issue Reporting

- Please use the provided issue templates for bug reports and feature requests.
- Before opening a new issue, check if a similar one already exists.

## Code Style

- We use `ruff` for Python formatting and linting.
- We use `prettier` for frontend, JSON, and markdown files.
- Ensure your changes pass all code quality checks before submitting a PR.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).
