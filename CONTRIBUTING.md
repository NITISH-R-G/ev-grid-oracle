# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues) to see if someone else in the community has already created a ticket. If not, go ahead and make one!

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

## Get the test suite running

Make sure to install the project and its dependencies:

```bash
uv pip install -e ".[dev,demo]"
```

Then run the test suite:

```bash
uv run pytest tests/
```

## Make sure tests pass

Before submitting a pull request, ensure all existing and new tests pass.

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## Create a pull request

Once your changes are complete, create a pull request against the `main` branch. A maintainer will review your code and may ask for some changes before merging it.

Thank you again for your contribution!
