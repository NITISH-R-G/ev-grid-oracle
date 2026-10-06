# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make Open Source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

## Get the test suite running

Make sure you have `uv` installed, as this project uses it for dependency management.

```bash
uv pip install -e ".[dev,demo]"
uv run pytest tests/
```

## Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch:

```bash
git remote add upstream https://github.com/NITISH-R-G/ev-grid-oracle.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```bash
git checkout <your-branch-name>
git rebase master
git push --set-upstream origin <your-branch-name>
```

Finally, go to GitHub and make a Pull Request.

## Code formatting and linting

This project uses `ruff` and `prettier` for code formatting and linting. Before committing your code, please ensure it passes all checks. We strongly recommend setting up `pre-commit` to run automatically before you commit:

```bash
pip install pre-commit
pre-commit install
```

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.
