# Contributing

First off, thank you for considering contributing to this repository. It's people like you that make open source such a great community!

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## 2. Fork & create a branch

If this is something you think you can fix, then fork the repository and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-new-feature
```

## 3. Get the test suite running

Make sure you're working in the correct virtual environment and that all dependencies are installed. We use `uv` for python dependency management.

```sh
uv pip install -e ".[dev,demo]"
```

Make sure the tests pass on your machine:

```sh
uv run pytest tests/
```

## 4. Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## 5. Validate your submission

We have a script to run the full suite of local submission checks, which includes ruff, mypy, bandit, and pytest.

```sh
./validate-submission.sh
```

If it fails to run due to missing modules, you can run the script via `uv` and add them as ephemeral dependencies:

```sh
uv run --with bandit --with mypy --with types-requests --with pytest --with pytest-asyncio --with matplotlib ./validate-submission.sh
```

## 6. Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with the main repository's master branch:

Then update your feature branch from your local copy of master, and push it!

Finally, go to GitHub and make a Pull Request!
