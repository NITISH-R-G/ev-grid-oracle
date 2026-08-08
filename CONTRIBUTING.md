# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open-source a great community.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please provide a clear and descriptive title and a detailed description of the proposed enhancement.

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible.
* End files with a newline.
* Place requires in the following order:
  * Built-in Node Modules (such as `path` or `fs`)
  * Local Modules (using relative paths)

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less

### Python Styleguide

* All Python code should be formatted using `ruff format`.
* Linting is enforced via `ruff check`.
* Type checking is enforced via `mypy`.
* Run `uv run pytest tests/` before submitting a PR.
