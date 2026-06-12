# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](https://github.com/your-username/ev-grid-oracle/issues) if one already exists. If not, go ahead and create one!

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-graphql-support
```

## Get the test suite running

Make sure you have `uv` and `npm` installed.

1. Clone your fork
2. Install dependencies:
    ```sh
    uv sync --all-extras
    cd web && npm install
    ```
3. Run Python tests:
    ```sh
    uv run pytest tests/
    ```
4. Run Frontend tests:
    ```sh
    cd web && npm test
    ```

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch:

```sh
git remote add upstream https://github.com/your-username/ev-grid-oracle.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 325-add-graphql-support
git rebase master
git push --set-upstream origin 325-add-graphql-support
```

Finally, go to GitHub and make a Pull Request!

## Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
