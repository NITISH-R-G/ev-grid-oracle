# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues) to see if someone else has already created a ticket. If not, go ahead and make one!

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```
git checkout -b 325-add-new-feature
```

## Setup the environment

We use `uv` for dependency management.

```bash
uv pip install -e ".[dev,demo]"
```

## Implementation guidelines

- Look at the `README.md` for project context.
- Write tests for your changes.
- Ensure your code follows the formatting rules (`ruff format` and `ruff check`).
- We enforce checks via `./validate-submission.sh`.

## Create a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch:

```bash
git remote add upstream git@github.com:NITISH-R-G/ev-grid-oracle.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```bash
git checkout 325-add-new-feature
git rebase master
git push --set-upstream origin 325-add-new-feature
```

Finally, go to GitHub and make a Pull Request!
