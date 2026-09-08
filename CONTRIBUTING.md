# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## 2. Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

## 3. Setting up the development environment

We use `uv` for dependency management.

```bash
pip install uv
uv pip install -e ".[dev,demo]"
```

## 4. Local Validation

Before submitting a Pull Request, you must run the local validation script. No code is merged unless it passes formatting, type checking, and test suites.

```bash
./validate-submission.sh
```

## 5. Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. Our autonomous PR agent and CI pipeline will review your request. Address any comments or test failures.
4. Once approved by our AI reviewer and human maintainers, your PR will be merged!
