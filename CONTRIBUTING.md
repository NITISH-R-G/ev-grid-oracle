# Contributing

Thank you for investing your time in contributing to our project!

Read our [Code of Conduct](./CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<your-username>/<repo>.git`
3. Create your feature branch: `git checkout -b my-new-feature`
4. Install dependencies:
   ```bash
   uv pip install --system -e ".[dev,demo]"
   ```
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin my-new-feature`
7. Submit a pull request.

## Development

The project uses `uv` for python dependency management and `npm` for the frontend.
Always run `./validate-submission.sh` before pushing your code to ensure tests, type checks, linting, and formatting pass.

### Tests

Tests are written using `pytest`. Run them with:

```bash
uv run pytest tests/
```

### Pre-commit Hooks

We use `pre-commit` to manage git hooks. Please make sure they are installed before you commit:

```bash
uv run pre-commit install
```
