import os

os.makedirs(".github/ISSUE_TEMPLATE", exist_ok=True)
os.makedirs(".github/workflows", exist_ok=True)
os.makedirs("tools", exist_ok=True)
os.makedirs("docs", exist_ok=True)
os.makedirs("artifacts", exist_ok=True)

# 1. CODEOWNERS
with open(".github/CODEOWNERS", "w") as f:
    f.write("* @NITISH-R-G\n")

# 2. CODE_OF_CONDUCT.md
with open("CODE_OF_CONDUCT.md", "w") as f:
    f.write("# Code of Conduct\n\nPlease treat everyone with respect.\n")

# 3. CONTRIBUTING.md
with open("CONTRIBUTING.md", "w") as f:
    f.write("# Contributing Guidelines\n\n1. Fork the repo.\n2. Create a branch.\n3. Make your changes.\n4. Run validation.\n5. Submit a PR.\n")

# 4. ISSUE_TEMPLATES
with open(".github/ISSUE_TEMPLATE/bug_report.md", "w") as f:
    f.write("---\nname: Bug Report\nabout: Create a report to help us improve\n---\n\n**Describe the bug**\n")
with open(".github/ISSUE_TEMPLATE/feature_request.md", "w") as f:
    f.write("---\nname: Feature Request\nabout: Suggest an idea for this project\n---\n\n**Is your feature request related to a problem?**\n")

# 5. greetings.yml
with open(".github/workflows/greetings.yml", "w") as f:
    f.write("""name: Greetings
on:
  pull_request_target:
    types: [opened]
  issues:
    types: [opened]

jobs:
  greeting:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
    - uses: actions/first-interaction@v1
      with:
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        issue-message: "Welcome to the repository! Thank you for opening your first issue."
        pr-message: "Welcome to the repository! Thank you for your first pull request."
""")

# 6. stale.yml
with open(".github/workflows/stale.yml", "w") as f:
    f.write("""name: Mark stale issues and pull requests
on:
  schedule:
  - cron: '30 1 * * *'

jobs:
  stale:
    runs-on: ubuntu-latest
    permissions:
      issues: write
      pull-requests: write
    steps:
    - uses: actions/stale@v9
      with:
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        stale-issue-message: 'This issue is stale because it has been open 30 days with no activity.'
        stale-pr-message: 'This PR is stale because it has been open 45 days with no activity.'
        days-before-stale: 30
        days-before-close: 7
""")

# 7. labeler.yml & .github/labeler.yml
with open(".github/workflows/labeler.yml", "w") as f:
    f.write("""name: Pull Request Labeler
on:
  pull_request_target:

jobs:
  triage:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
    - uses: actions/labeler@v5
      with:
        repo-token: "${{ secrets.GITHUB_TOKEN }}"
""")

with open(".github/labeler.yml", "w") as f:
    f.write("""python:
  - all:
    - changed-files:
      - any-glob-to-any-file: '**/*.py'
frontend:
  - all:
    - changed-files:
      - any-glob-to-any-file: ['web/**', '**/*.ts', '**/*.tsx']
docs:
  - all:
    - changed-files:
      - any-glob-to-any-file: '**/*.md'
""")

# 8. ai-review.yml
with open(".github/workflows/ai-review.yml", "w") as f:
    f.write("""name: AI PR Agent

on:
  pull_request:
    types: [opened, synchronize, reopened]
  pull_request_review_comment:
    types: [created]
  issue_comment:
    types: [created]

jobs:
  pr_reviewer:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - name: CodeRabbit AI PR Review
        uses: coderabbitai/openai-pr-reviewer@latest
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        with:
          debug: false
          review_simple_changes: false
          review_comment_lgtm: false
""")

# 9. codeql.yml
with open(".github/workflows/codeql.yml", "w") as f:
    f.write("""name: "CodeQL"

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '0 0 * * 0'

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'python', 'javascript' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v3

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v3
""")
