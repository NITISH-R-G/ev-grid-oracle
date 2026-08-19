# Contributing Guidelines

Thank you for your interest in contributing to this project!

## How to Contribute

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/YOUR-FORK.git`
3. Create a branch: `git checkout -b feature-or-bugfix-name`
4. Make your changes and commit them: `git commit -m "Description of changes"`
5. Push to your fork: `git push origin feature-or-bugfix-name`
6. Create a Pull Request against the main repository

## Development Setup

We use `uv` for Python dependency management.

```bash
uv pip install -e ".[dev,demo]"
```

## Testing

Ensure tests pass before submitting a pull request:

```bash
uv run pytest tests/
```

## Formatting and Linting

We enforce `ruff` for code formatting and linting:

```bash
uv run ruff check . --fix
uv run ruff format .
```

## Pull Request Guidelines

- Keep PRs small and focused.
- Ensure the CI checks pass.
- Write a clear and descriptive commit message.
