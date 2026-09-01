# Contributing Guidelines

First off, thank you for considering contributing to this repository. It's people like you that make this open-source project such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](../../issues) to see if someone else in the community has already created a ticket. If not, go ahead and make one!

## Fork & create a branch

If this is something you think you can fix, then fork the repository and create a branch with a descriptive name.

## Get the test suite running

Make sure to install the required development and testing dependencies, e.g. `pip install -e ".[dev]"`. Ensure the tests are passing before creating a PR by running the `./validate-submission.sh` script or `pytest tests/`.

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with the main repository's main branch.

Then create a pull request with a clear title and description against the `main` branch.

## CI Checks

Ensure all CI checks pass. We use automated processes for checking code quality, formatting, security, and tests.

Thank you!
