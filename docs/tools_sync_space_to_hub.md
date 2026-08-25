# Documentation for `tools/sync_space_to_hub.py`

## Module Docstring

Push this repo to a Hugging Face *Space* without using `git push` (avoids Hub binary rejections).

Docker Spaces often have **no** “link GitHub repo” in Settings — the Space is its own Hub git repo.
Use this script after `git push origin main`; it uploads sources + a fresh `web/dist` via the Hub API.

Usage:
  cd repo root
  npm --prefix web run build    # or let this script run it (default)
  python tools/sync_space_to_hub.py

Requires: `pip install huggingface_hub`, token with write access (`HF_TOKEN` or `huggingface-cli login`).

## Function: `main`
