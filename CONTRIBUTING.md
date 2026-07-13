# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! We welcome all contributions and aim to make it as easy as possible to contribute.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

*   **Use a clear and descriptive title.**
*   **Describe the exact steps which reproduce the problem** in as many details as possible.
*   **Provide specific examples to demonstrate the steps.**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Before creating enhancement suggestions, please check existing issues.

*   **Use a clear and descriptive title.**
*   **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
*   **Explain why this enhancement would be useful** to most users.

### Pull Requests

*   **Local Validation:** Before opening a PR, ensure you have run `./validate-submission.sh`. All linting (`ruff`), type checking (`mypy`), security checks (`bandit`), and tests (`pytest`) must pass.
*   **Documentation:** Update the README.md with details of changes to the interface, if applicable.
*   **Commit Messages:** Write clear, concise commit messages.

## Development Setup

1.  **Clone the repo:** `git clone https://github.com/NITISH-R-G/ev-grid-oracle.git`
2.  **Navigate into the directory:** `cd ev-grid-oracle`
3.  **Install dependencies:** We use `uv`. Run `uv pip install -e ".[dev,demo]"` to install all required dependencies.
4.  **Run tests:** `uv run pytest tests/`

## Governance

This project is primarily maintained by `@NITISH-R-G`. We use an autonomous PR agent and CI/CD pipelines to ensure code quality. Reviewers will check your code before it can be merged.
