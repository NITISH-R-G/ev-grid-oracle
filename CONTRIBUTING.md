# Contributing

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to this repository. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Please provide a clear and descriptive title and a detailed description of the proposed enhancement.

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the Python coding style used throughout the project
* End all files with a newline
* Run the tests and validation suite before submitting `uv run ./validate-submission.sh`

## Development Environment Setup

1. Make sure you have python 3.10 or later installed.
2. We use `uv` for package management. Please install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`.
3. Install dependencies: `uv pip install -e ".[dev,demo]"`
4. Make sure to setup `pre-commit` hooks if they are configured.

## Styleguides

### Git Commit Messages
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
