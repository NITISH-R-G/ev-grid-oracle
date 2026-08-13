# Contributing Guidelines

First off, thank you for considering contributing to our project! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our Issues to see if someone else has already created an issue for it. If not, feel free to open a new one.

## Setting up your environment

1.  Fork the repo and clone it to your local machine.
2.  Install `uv` if you haven't already.
3.  Run `uv pip install -e ".[dev,demo]"` to install all required development, test, and demo dependencies.
4.  For frontend work, `cd web` and run `npm install`.

## Making Changes

*   Create a new branch from `main`.
*   Make your changes.
*   Ensure all tests pass by running `uv run pytest tests/`.
*   Ensure code quality by running formatting and linting tools (`ruff`, `mypy`, etc.).
*   Run `./validate-submission.sh` locally before submitting a PR.
*   Commit your changes with clear, descriptive commit messages.

## Submitting a Pull Request

*   Push your branch to your fork.
*   Open a Pull Request against the `main` branch of this repository.
*   Provide a detailed description of your changes and why they are necessary.
*   Link to any relevant issues.
*   Wait for review and address any feedback!

We appreciate your contributions and look forward to working with you!
