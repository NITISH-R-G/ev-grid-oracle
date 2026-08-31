# Contributing Guidelines

Thank you for your interest in contributing to our project! We welcome and appreciate all contributions.

## How to Contribute

1. **Fork the Repository**: Start by forking the repo and cloning it locally.
2. **Setup the Environment**: Follow the instructions in the README to set up the development environment using `uv`.
3. **Create a Branch**: Create a new branch for your feature or bugfix.
4. **Make Changes**: Implement your changes. Please ensure you include tests for any new functionality.
5. **Format and Lint**: Run `ruff check .` and `ruff format .` to ensure your code matches our style guidelines.
6. **Submit a Pull Request**: Push your branch to GitHub and open a pull request against the `main` branch.

## Pull Request Process

* Ensure any install or build dependencies are removed before the end of the layer when doing a build.
* Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
* You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Development Workflows

We heavily utilize GitHub actions for autonomous maintenance (e.g. generating docs, architecture diagrams, etc). When you push code, these workflows will run automatically to keep the repository healthy and up to date.

Thank you again for contributing to our community!
