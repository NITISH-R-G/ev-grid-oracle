# Contributing to OpenEnv

First off, thank you for considering contributing to OpenEnv. It's people like you that make OpenEnv such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## Fork & create a branch

If this is something you think you can fix, then fork OpenEnv and create a branch with a descriptive name.

## Get the test suite running

Make sure you're using `uv` to manage the environment:

```bash
uv sync --all-extras
uv run pytest tests/
```

## Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with OpenEnv's master branch:

```bash
git remote add upstream https://github.com/NITISH-R-G/OpenEnv.git
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```bash
git checkout 325-add-japanese-translations
git rebase master
git push --set-upstream origin 325-add-japanese-translations
```

Finally, go to GitHub and make a Pull Request.

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.
