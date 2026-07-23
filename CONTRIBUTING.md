# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle!

## Development Setup

The project uses `uv` for Python dependency management and `npm` for the frontend web application.

To set up the development environment, make sure you have `uv` installed.

### Python Environment
To install all required dependencies (including dev, demo, and others), run:
```bash
uv pip install -e ".[dev,demo]"
```
or
```bash
uv sync --all-extras
```

### Frontend Environment
Navigate to the `web` directory and use npm:
```bash
cd web
npm install
```

## Submitting Pull Requests

1. Fork the repository and create your branch from `main`.
2. Ensure you have tested your changes.
3. Make sure code meets formatting standards:
    - We use `ruff` for python code: `uv run --with ruff ruff check --fix .` and `uv run --with ruff ruff format .`
    - Make sure to pass mypy tests.
    - Check for duplicates/complexity.
    - For the frontend, run `npx prettier --check .` and ensure types are verified with `npx tsc --noEmit`.
4. Ensure tests pass by running `./validate-submission.sh`.
5. Issue that pull request!

## Need Help?
Check out our extensive documentation or create an issue. Let's build the best EV Grid simulator together!
