# Contributing to this project

First off, thank you for considering contributing to this project!

## Development Setup

We use `uv` for dependency management.

1. Install `uv`: `pip install uv`
2. Install dependencies: `uv pip install -e ".[dev,demo]"`

### Frontend

1. Navigate to the `web` directory: `cd web`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`

## Guidelines

- All PRs must pass CI checks.
- Code must be formatted and pass linting (`ruff format .` and `ruff check .`).
- Add tests for new features.
- Please write descriptive commit messages and PR descriptions.
