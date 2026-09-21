# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues) to see if someone else in the community has already created a ticket. If not, go ahead and make one!

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

## Get the test suite running

Make sure you're using a virtual environment (we recommend `uv`). Install dependencies and run tests:

```bash
uv pip install -e ".[dev,demo]"
uv run pytest tests/
```

## Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first.

## Code Quality and Formatting

We use `ruff` for formatting and linting. Please make sure your code passes these checks before opening a pull request.

```bash
ruff check .
ruff format .
```

## Make a Pull Request

At this point, you should switch back to your master branch, make sure it's up to date with EV Grid Oracle's master branch.
Then push your changes and create a pull request.
