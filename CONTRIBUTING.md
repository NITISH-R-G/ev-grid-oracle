# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make it such a great project.

## Code of Conduct

This project and everyone participating in it is governed by the [EV Grid Oracle Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible according to the template.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Please provide a clear description and context for your suggestion.

### Pull Requests

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes (`uv run pytest`).
5. Make sure your code lints (`uv run ruff check .`).
6. Issue that pull request!

## Local Development

The project uses `uv` for dependency management.

```bash
uv pip install -e ".[dev,demo]"
uv run pytest tests/
```
