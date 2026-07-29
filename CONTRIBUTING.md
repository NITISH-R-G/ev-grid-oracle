# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make Open Source such a great community.

## Where to start

* **Bugs**: If you spot a bug, please create a bug report using the template provided.
* **Features**: Have a great idea for a new feature? Create a feature request issue!
* **Code**: Look for issues labeled `good first issue` or `help wanted` if you want to jump straight into coding.

## Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Validate your changes locally: `./validate-submission.sh`
5. Commit your changes: `git commit -m "feat: description of changes"`
6. Push to your branch: `git push origin feature-name`
7. Open a Pull Request

## Requirements

* **Type Checking**: We use `mypy`. Ensure your code passes type checking.
* **Linting/Formatting**: We use `ruff`. Run `ruff check .` and `ruff format .`.
* **Testing**: Write tests for your changes. Run `pytest tests/`.
* All tests and checks are required to pass before merging.

Thank you for contributing!
