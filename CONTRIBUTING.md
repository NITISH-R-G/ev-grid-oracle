# Contributing Guidelines

First off, thank you for considering contributing to this repository. It's people like you that make open-source such a great community!

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make one! It's generally best if you get confirmation of your bug or approval for your feature request this way before starting to code.

## 2. Setting up the environment

The project uses `uv` for Python dependency management. You can set up your local environment and install all required development, test, and demo dependencies with:

```bash
uv pip install -e ".[dev,demo]"
```

For the frontend web project, make sure to use Node.js 24 and install dependencies:

```bash
cd web
npm ci
```

## 3. Creating a Pull Request

1. Fork the repository and create your branch from `main`.
2. Make sure you've added tests for your changes.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes: `./validate-submission.sh`
5. Issue a pull request!

## 4. Code Quality and Maintenance

We rely heavily on autonomous checks.

### Pre-commit
A `.pre-commit-config.yaml` is enforced locally for contributors. We use `ruff` for Python linting/formatting and `prettier` for frontend/JSON/markdown formatting.

To ensure your code meets quality standards, you can run the validation script:

```bash
./validate-submission.sh
```

## 5. Automated Autonomous Tools

The repository includes tools for maintaining health and documentation natively:
- `tools/generate_health_dashboard.py`
- `tools/generate_knowledge_graph.py` (autonomous knowledge graph generation)
- `tools/docs_sync.py` (documentation synchronization)

These generate artifacts that you do not need to commit manually, our AI Actions and automated pipelines handle this seamlessly.

Thanks for contributing!
