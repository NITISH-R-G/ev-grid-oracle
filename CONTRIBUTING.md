# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open-source a great community to learn, inspire, and create.

## How Can I Contribute?

### Reporting Bugs

- **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/NITISH-R-G/ev-grid-oracle/issues).
- If you're unable to find an open issue addressing the problem, open a new one using the Bug Report template.

### Suggesting Enhancements

- Open a new issue using the Feature Request template.
- Provide a clear description and any mockups or diagrams if applicable.

### Pull Requests

1. **Fork the repository** and create your branch from `main`.
2. **Make your changes**. Ensure your code is clean and well-documented.
3. **Run validation checks** locally before submitting:
   ```bash
   ./validate-submission.sh
   ```
4. **Create a Pull Request** with a detailed description of your changes.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NITISH-R-G/ev-grid-oracle.git
   cd ev-grid-oracle
   ```
2. **Install dependencies:**
   We use `uv` for dependency management.
   ```bash
   uv pip install -e ".[dev,demo]"
   ```
3. **Run tests:**
   ```bash
   uv run pytest tests/
   ```

## Coding Standards

- **Python:** We strictly follow PEP 8. Use `ruff` for linting and formatting. Ensure 100% type safety using `mypy`.
- **Frontend:** Use Prettier for formatting and TypeScript for type safety.

Thank you for contributing!
