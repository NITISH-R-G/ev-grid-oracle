# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## 2. Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```bash
git checkout -b 325-add-new-feature
```

## 3. Local Development Setup

We use `uv` for dependency management and Python environments.

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ev-grid-oracle.git
cd ev-grid-oracle

# Install all development and test dependencies
uv pip install -e ".[dev,demo]"

# Run frontend tests
cd web && npm ci && npm test
```

## 4. Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first.

*   Follow the style of the existing code.
*   Make sure you add/update tests for your changes.

## 5. Validate your submission

Before committing or opening a PR, run the local validation script. This ensures your code meets our quality standards (formatting, linting, type-checking, and tests).

```bash
./validate-submission.sh
```

## 6. Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch.

Then push your feature branch to your fork and create a Pull Request! We'll review your code and give you feedback as soon as possible.
