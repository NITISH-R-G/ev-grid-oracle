#!/usr/bin/env python3
"""
Generates architecture diagrams using pydeps.
Requires: pip install pydeps xdg-utils
"""

import os
import subprocess  # nosec B404
import sys


def main() -> None:
    # Ensure pydeps is installed in the current environment
    try:
        import pydeps  # type: ignore
    except ImportError:
        print(
            "pydeps not found. Installing pydeps and xdg-utils is recommended.",
            file=sys.stderr,
        )
        # Attempt to continue, let subprocess fail if pydeps executable is not in PATH

    os.makedirs("docs", exist_ok=True)

    targets = [
        ("ev_grid_oracle", "docs/ev_grid_oracle_architecture.svg"),
        ("server", "docs/server_architecture.svg"),
    ]

    for target_dir, out_file in targets:
        if not os.path.exists(target_dir):
            continue

        cmd = ["pydeps", target_dir, "--noshow", "--format=svg", f"-o={out_file}"]

        try:
            print(f"Generating architecture diagram for {target_dir}...")
            subprocess.run(cmd, check=True)  # nosec B603
            print(f"Saved diagram to {out_file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate diagram for {target_dir}: {e}", file=sys.stderr)
        except FileNotFoundError:
            print(
                "pydeps command not found in PATH. Make sure it is installed.",
                file=sys.stderr,
            )
            break


if __name__ == "__main__":
    main()
