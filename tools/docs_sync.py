#!/usr/bin/env python3
import os
from pathlib import Path


def sync_docs():
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    # Generate a simple dynamic index
    index_path = docs_dir / "index.md"
    index_content = "# EV Grid Oracle Documentation\n\n## Auto-generated API Index\n\n"

    for root, _, files in os.walk(repo_root):
        if (
            ".git" in root
            or "node_modules" in root
            or "venv" in root
            or ".venv" in root
            or "docs" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_root)
                index_content += f"- [{rel_path}](../{rel_path})\n"

    with open(index_path, "w") as f:
        f.write(index_content)

    print(f"Docs synced. Updated {index_path}")


if __name__ == "__main__":
    sync_docs()
