# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make it a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our issues first. If it doesn't exist, feel free to open a new one.

## Setting up your environment

1. Clone the repository.
2. Install Python dependencies using `uv`: `uv pip install -e ".[dev,demo]"`
3. Install frontend dependencies: `cd web && npm install`
4. Run tests: `python -m pytest tests/`

## Making Changes

* Create a new branch for your feature or bug fix.
* Write tests for your changes.
* Ensure all tests pass.
* Run our validation script before committing: `./validate-submission.sh`
* Submit a pull request.
