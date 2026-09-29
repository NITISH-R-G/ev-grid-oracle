# Contributing

Welcome to this repository! We appreciate your help to make this project better.

## Development Setup

We use `uv` for Python dependency management.
```bash
uv pip install -e ".[dev,demo]"
```

For the frontend, we use Vite + TypeScript.
```bash
cd web && npm ci
```

## Making Changes
- Make sure to create a branch for your feature or bug fix.
- Add tests where necessary.
- Follow code style guidelines (we use `ruff` and `prettier`).
- Run `./validate-submission.sh` before submitting a PR to verify all checks pass locally.
