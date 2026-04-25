#!/usr/bin/env bash
# Local submission checks: pytest + optional openenv validate + optional Docker.
# Writes a timestamped log to assets/validation_output.txt (for judge / audit trail).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
mkdir -p "$ROOT/assets"
OUT="$ROOT/assets/validation_output.txt"

{
  echo "=== EV Grid Oracle — validate-submission ==="
  date -u +"%Y-%m-%dT%H:%MZ (UTC)"
  echo "repo: $ROOT"
  echo "--- python ---"
  python --version
  echo "--- pytest (install dev deps first: pip install -e \".[dev]\") ---"
  python -m pytest tests/ -q --tb=line
  if command -v openenv >/dev/null 2>&1; then
    echo "--- openenv validate ---"
    openenv validate "$ROOT/openenv.yaml"
  else
    echo "--- openenv validate (skipped: openenv not on PATH) ---"
  fi
  if [[ "${VALIDATE_DOCKER:-0}" == "1" ]]; then
    echo "--- docker build (repo root Dockerfile) ---"
    docker build -t ev-grid-oracle-validate:local "$ROOT"
  else
    echo "--- docker build (skipped; set VALIDATE_DOCKER=1 to enable) ---"
  fi
  echo "=== OK ==="
} | tee "$OUT"

echo "Wrote $OUT"
