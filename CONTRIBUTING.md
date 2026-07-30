# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle! It's people like you that make open source such a great community.

## Development Setup
We recommend using `uv` for python dependency management.

1. Install dependencies:
   ```bash
   uv pip install -e ".[dev,demo]"
   ```
2. Build frontend:
   ```bash
   cd web
   npm ci
   npm run build
   ```
3. Run tests locally:
   ```bash
   ./validate-submission.sh
   ```

## Pull Request Process
1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

Thank you!
