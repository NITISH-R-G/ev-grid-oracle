# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great project.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check a list of [open issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible according to the provided issue template.

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues). When you are creating an enhancement suggestion, please include as many details as possible according to the provided issue template.

### Pull Requests

* Fill in the required template.
* Do not include issue numbers in the PR title.
* Include screenshots and animated GIFs in your pull request whenever possible.
* Follow the Python styleguide.
* Document new code based on the Documentation Styleguide.
* Run the tests!

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* All Python must adhere to `ruff` linting and formatting standards.
* All Python must pass strict type-checking using `mypy`.
* Code must be documented according to Google Python Style Guide.

## Automated Verification

Run `./validate-submission.sh` before submitting any PR. This script checks:
* Formatting (ruff)
* Linting (ruff)
* Type safety (mypy)
* Security (bandit)
* Tests (pytest)

No code will be accepted unless it passes these automated checks.
