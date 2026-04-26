#!/usr/bin/env python3
"""
Push this repo to a Hugging Face *Space* without using `git push` (avoids Hub binary rejections).

Docker Spaces often have **no** “link GitHub repo” in Settings — the Space is its own Hub git repo.
Use this script after `git push origin main`; it uploads sources + a fresh `web/dist` via the Hub API.

Usage:
  cd repo root
  npm --prefix web run build    # or let this script run it (default)
  python tools/sync_space_to_hub.py

Requires: `pip install huggingface_hub`, token with write access (`HF_TOKEN` or `huggingface-cli login`).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Globs for upload_folder — keep repo lean for Space; never ship huge artifacts here.
DEFAULT_IGNORE = [
    ".git/**",
    "**/__pycache__/**",
    "**/*.pyc",
    ".venv/**",
    "web/node_modules/**",
    "artifacts/**",
    ".superpowers/**",
    ".cursor/**",
    "terminals/**",
    "*.egg-info/**",
    ".pytest_cache/**",
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Upload repo tree to HF Space (skips artifacts / node_modules).")
    ap.add_argument(
        "--repo-id",
        default=os.environ.get("HF_SPACE_REPO_ID", "NITISHRG15102007/ev-grid-oracle"),
        help="Space repo id (namespace/name)",
    )
    ap.add_argument("--skip-build", action="store_true", help="Do not run npm run build in web/")
    args = ap.parse_args()

    if not args.skip_build:
        print("Running: npm --prefix web run build...")
        npm = "npm.cmd" if os.name == "nt" else "npm"
        subprocess.run([npm, "--prefix", "web", "run", "build"], cwd=ROOT, check=True)

    from huggingface_hub import HfApi

    api = HfApi()
    print(f"Uploading {ROOT} -> {args.repo_id} (repo_type=space), ignoring heavy paths...")
    info = api.upload_folder(
        repo_id=args.repo_id,
        folder_path=str(ROOT),
        repo_type="space",
        ignore_patterns=DEFAULT_IGNORE,
        commit_message="sync: push from tools/sync_space_to_hub.py (no artifacts/)",
    )
    print("Done:", info)
    print("Next: Space Settings -> Restart or Factory rebuild if the container does not pick up static files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
