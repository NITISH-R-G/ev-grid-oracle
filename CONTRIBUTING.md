# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make EV Grid Oracle such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](../../issues) to see if someone else has already created a ticket. If not, go ahead and [make one](../../issues/new)!

## Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

## Get the test suite running

Make sure to install the project and run the tests:
```bash
uv pip install -e ".[dev,demo]"
./validate-submission.sh
```

## Implement your fix or feature

At this point, you're ready to make your changes! Feel free to ask for help; everyone is a beginner at first.

## Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch.
Then run a git rebase on your branch:
```bash
git rebase master
```

Then push your branch and open a PR!
