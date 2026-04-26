#!/usr/bin/env python3
"""Run a tiny paired evaluate.py job and write artifacts/eval_snapshot.json (no LLM)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out = root / "artifacts" / "eval_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "ORACLE_SKIP_LLM": "1"}
    cmd = [
        sys.executable,
        str(root / "training" / "evaluate.py"),
        "--episodes",
        "2",
        "--seed",
        "777",
        "--scenario",
        "baseline",
        "--out",
        str(out),
    ]
    subprocess.run(cmd, check=True, cwd=str(root), env=env)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
