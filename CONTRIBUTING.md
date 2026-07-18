# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## 2. Fork & create a branch

If this is something you think you can fix, then fork EV Grid Oracle and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-new-feature
```

## 3. Local Development

Ensure you use `./validate-submission.sh` for any local development.

```bash
# Setup
uv pip install -e ".[dev,demo]"

# Run validation
./validate-submission.sh
```

## 4. Pull Request

When you're ready to create a pull request, be sure to:

- Have test cases for the new code. If you have questions about how to do this, please ask in your pull request.
- Run the `./validate-submission.sh` script to ensure everything passes locally.
- Write a good commit message.
- Fill out the PR template.

## Continuous Engineering & Agile Workflow

This repository strictly follows an Agile Scrum continuous improvement methodology. Our objective is to treat this repository as a living, elite engineering product. Every improvement cycle operates on a fixed loop.

To participate, contributors must respect local validation tools. No code is merged unless it passes formatting, type checking, and test suites.