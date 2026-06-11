# Contributing Guidelines

Welcome! We are thrilled that you'd like to contribute. This repository operates as an autonomous, self-improving open-source ecosystem.

## Autonomous Systems

When you open an issue or PR, our AI maintainer will review your code, run formatting checks (and automatically fix them if possible), and ensure test coverage.

## Development Setup

We use `uv` for Python dependency management and `npm` for the frontend.

```bash
uv sync --all-extras
cd web && npm install
```

## Pull Requests

1. Fork the repo and create your branch from `main`.
2. Ensure you have added tests that prove your fix is effective or that your feature works.
3. Our CI will automatically run formatting (`ruff`, `prettier`) and static analysis.
4. An AI reviewer will provide insights.

Thank you for contributing!
