1. Set up Community Health Files:
   - Create `CODE_OF_CONDUCT.md`
   - Create `CONTRIBUTING.md`
   - Create `.github/CODEOWNERS` (assigned to `@NITISH-R-G`)
   - Create Issue Templates (`bug_report.yml`, `feature_request.yml`) and `PULL_REQUEST_TEMPLATE.md`
2. Create python maintenance tools:
   - `tools/generate_knowledge_graph.py` to parse files and build knowledge graph
   - `tools/docs_sync.py` to sync docstrings and update documentation files
3. Create new workflows for automated project management:
   - `.github/workflows/greetings.yml`
   - `.github/workflows/stale.yml`
   - `.github/workflows/labeler.yml` and `.github/labeler.yml`
   - `.github/workflows/ai-review.yml` (using `coderabbitai/coderabbit-pr-review`)
   - `.github/workflows/ci.yml` for Continuous Integration
4. Consolidate autonomous generation workflows into `.github/workflows/repo-maintenance.yml`:
   - Runs on push to main or pull request
   - Runs autofix (ruff fix/format)
   - Generates architecture diagrams (using pydeps)
   - Generates knowledge graph
   - Syncs docs
   - Generates SBOM (using cyclonedx-py)
   - Commits changes back to the branch
5. Pre commit checks
