# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make this tool such a great project.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

* Use the Bug Report issue template.
* Explain the problem and include additional details to help maintainers reproduce the problem.
* Provide specific examples to demonstrate the steps. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion.

* Use the Feature Request issue template.
* Provide a step-by-step description of the suggested enhancement in as many details as possible.
* Explain why this enhancement would be useful to most users.

### Pull Requests

* Fill in the required template.
* Do not include issue numbers in the PR title.
* Include screenshots and animated GIFs in your pull request whenever possible.
* Follow the Python coding style guidelines (PEP 8).
* End all files with a newline.
* Ensure the test suite passes locally (`./validate-submission.sh`).
* Ensure code quality checks (Ruff, MyPy) pass.

## Development Setup

1. Fork the repo and create your branch from `main`.
2. Ensure you have Python and `uv` installed.
3. Install dependencies: `uv pip install -e ".[dev,demo]"`
4. Run tests: `uv run pytest tests/`
5. Make sure `./validate-submission.sh` passes before submitting a PR.
