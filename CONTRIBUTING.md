# Contributing to the Repository

First off, thank you for considering contributing to this repository! It's people like you that make open source such a great community.

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check our [Issues](../../issues) to see if someone else has already created a ticket. If not, go ahead and create one!

## 2. Fork & create a branch

If this is something you think you can fix, then fork the repository and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```
git checkout -b 325-add-new-feature
```

## 3. Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first!

## 4. Run local tests and validation

Before committing, please ensure that your code passes all local validation scripts.
Run the local validation script:

```bash
./validate-submission.sh
```

## 5. Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with the main repository's master branch.

Then push your branch to GitHub and create a Pull Request against the main repository.

## 6. Keeping your Pull Request updated

If a maintainer asks you to rebase your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

## 7. Automated Reviews and Actions

Once you submit a PR, our automated CI/CD and AI-powered reviewers will check your code. Please address any comments left by the bots or human reviewers.

Thank you!
