# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues) if one already exists. If not, you can open a new issue.

## Setting up your environment

1.  **Fork the repo** and clone it locally.
2.  **Install dependencies** using `uv`:
    ```bash
    uv pip install -e ".[dev,demo]"
    ```
3.  **Run tests** to ensure everything is working:
    ```bash
    uv run pytest tests/
    ```

## Development Workflow

1.  Create a branch for your feature or bug fix.
2.  Make your changes.
3.  Run linters and formatters:
    ```bash
    uv run ruff check --fix .
    uv run ruff format .
    ```
4.  Run tests to verify changes:
    ```bash
    uv run pytest tests/
    ```
5.  Submit a Pull Request. Our CI and AI Reviewer will provide feedback.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
