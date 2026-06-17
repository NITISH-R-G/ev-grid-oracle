# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great tool.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone the project** to your own machine.
3.  **Install dependencies**:
    - The project uses `uv` for Python dependency management.
    - Run `uv sync --all-extras` or `uv pip install -e ".[dev]"` to set up the virtual environment and install all required development and test dependencies.
    - For the frontend, navigate to `web/` and run `npm install`.

## Development Workflow

1.  **Create a branch** for your feature or bug fix (`git checkout -b feature/your-feature-name`).
2.  **Make your changes**.
3.  **Ensure all tests pass**:
    - Python: Run `uv run pytest tests/`.
    - Frontend: Navigate to `web/` and run `npm test`.
    - Note: Frontend mapping components require robust mocks (e.g., `maplibre-gl`, `canvas`).
4.  **Run validation script**:
    - Execute `./validate-submission.sh` in the root directory to run the full suite of local submission checks, including formatting, linting, type-checking, and tests.
5.  **Commit your changes** with descriptive commit messages.

## Pull Requests

1.  **Push your changes** to your fork.
2.  **Open a Pull Request** against the `main` branch.
3.  Ensure your PR title is descriptive and follows conventional commit format if possible.
4.  Fill out the pull request template and link any relevant issues.
5.  All PRs are subject to review by AI and human maintainers.

## Code Quality Standards

- **Python**: We use `ruff` for linting and formatting, `mypy` for type checking, and `bandit` for security scanning. These are enforced locally via `.pre-commit-config.yaml` and our CI pipeline.
- **Frontend**: We use `prettier` for formatting and TypeScript for type checking.
- **Security**: Do not use `secrets.SystemRandom` for deterministic PRNG needs; use a cryptographic hash approach (like `hashlib.sha256`) to derive sequence values. Extract sensitive credentials early and remove them from the global environment using `os.environ.pop()`.

## Issue Reporting

- Use the provided issue templates for bug reports and feature requests.
- Provide as much detail as possible, including steps to reproduce bugs and expected vs. actual behavior.

Thank you for contributing!
