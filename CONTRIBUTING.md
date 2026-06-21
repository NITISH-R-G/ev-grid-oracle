# Contributing to EV Grid Oracle

First off, thank you for considering contributing to EV Grid Oracle. It's people like you that make this an advanced, self-improving open-source repository.

## 1. Where do I go from here?

If you've noticed a bug or have a feature request, please make sure to check our [issue tracker](https://github.com/your-org/ev-grid-oracle/issues) to see if someone else in the community has already created a ticket. If not, go ahead and [make one](https://github.com/your-org/ev-grid-oracle/issues/new/choose)!

## 2. Fork & create a branch

If this is something you think you can fix, then [fork EV Grid Oracle](https://help.github.com/articles/fork-a-repo) and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-graphql-support
```

## 3. Get the test suite running

Make sure you have a working development environment. We use `uv` for Python dependencies and `npm` for the frontend.

```sh
# Install Python dependencies
uv pip install -e ".[dev,demo]"

# Run tests
pytest tests/
```

For the frontend:
```sh
cd web
npm install
npm test
```

## 4. Implement your fix or feature

At this point, you're ready to make your changes. Feel free to ask for help; everyone is a beginner at first.

## 5. Make a Pull Request

At this point, you should switch back to your master branch and make sure it's up to date with EV Grid Oracle's master branch:

```sh
git remote add upstream git@github.com:your-org/ev-grid-oracle.git
git checkout master
git pull upstream master
```

Then update your feature branch from your local copy of master, and push it!

```sh
git checkout 325-add-graphql-support
git rebase master
git push --set-upstream origin 325-add-graphql-support
```

Finally, go to GitHub and [make a Pull Request](https://help.github.com/articles/creating-a-pull-request) :D

## 6. Keeping your Pull Request updated

If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

## Additional Guidelines

- Follow existing style.
- The project is heavily automated. Expect AI PR reviews, automated linting/formatting fixes, and continuous health dashboard updates.
- Adhere to the Code of Conduct.

Thank you!
