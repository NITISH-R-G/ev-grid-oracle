# Contributing Guidelines

Thank you for investing your time in contributing to our project!

## Getting Started

1.  **Fork the repository:** Click the "Fork" button on the top right of this page.
2.  **Clone your fork:** `git clone https://github.com/<your-username>/<repo-name>.git`
3.  **Create a branch:** `git checkout -b feature/your-feature-name`

## Development Environment Setup

This project uses `uv` for dependency management.

```bash
uv pip install -e ".[dev,demo]"
```

## Making Changes

*   Write clean, readable code.
*   Follow the existing code style. The project uses `ruff` for linting and formatting, and `prettier` for frontend files.
*   Run tests before submitting a PR: `uv run pytest tests/`
*   Add tests for any new features or bug fixes.

## Submitting a Pull Request

1.  **Commit your changes:** Write a clear and descriptive commit message.
2.  **Push to your fork:** `git push origin feature/your-feature-name`
3.  **Open a Pull Request:** Go to the original repository and click "New pull request".
4.  **Fill out the PR template:** Provide as much detail as possible about your changes.
5.  **Wait for review:** Maintainers (or our AI assistant) will review your PR and provide feedback.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
