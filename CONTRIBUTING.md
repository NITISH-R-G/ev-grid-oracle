# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues) if it has already been reported or requested. If not, open a new issue!

## Development Environment Setup

1.  **Fork** the repo on GitHub
2.  **Clone** the project to your own machine
3.  **Install requirements** (using `uv`):
    ```bash
    uv pip install -e ".[dev,demo]"
    ```
4.  **Run tests**:
    ```bash
    pytest tests/
    ```

## Submitting a Pull Request

1.  Create a new branch for your feature or bug fix.
2.  Commit your changes with clear, descriptive commit messages.
3.  Push your branch to your fork.
4.  Submit a Pull Request targeting the `main` branch.
5.  Make sure your code passes all CI checks. Our autonomous systems will review your PR and may provide feedback or automated fixes.

## Code Quality Standards

*   We use `ruff` for linting and formatting. Run `ruff check . --fix` and `ruff format .` before committing.
*   We use `mypy` for type checking. Ensure all new code is type-annotated.
*   Write tests for new features and bug fixes using `pytest`.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
