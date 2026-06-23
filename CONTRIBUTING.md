# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our Issues if it has already been reported/requested. If not, open a new issue.

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

## Get the test suite running

Make sure you have `uv` installed, then run:

```bash
uv pip install -e ".[dev,demo]"
```

Run tests using:

```bash
pytest tests/
```

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch.
Then update your feature branch from your local copy of master, and push it!
Finally, go to GitHub and make a Pull Request.
