#!/usr/bin/env python3
"""Autonomous Knowledge Graph generator."""

import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_knowledge_graph(repo_root: Path, output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    info: dict[str, list[dict[str, Any]]] = {
        "files": [],
        "classes": [],
        "functions": [],
    }

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = Path(root) / file
            rel_path = str(filepath.relative_to(repo_root))

            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                module = ast.parse(content)
                info["files"].append({"id": rel_path, "type": "file", "path": rel_path})

                for node in ast.walk(module):
                    if isinstance(node, ast.ClassDef):
                        info["classes"].append(
                            {
                                "id": f"{rel_path}:{node.name}",
                                "name": node.name,
                                "file": rel_path,
                                "type": "class",
                            }
                        )
                    elif isinstance(node, ast.FunctionDef):
                        info["functions"].append(
                            {
                                "id": f"{rel_path}:{node.name}",
                                "name": node.name,
                                "file": rel_path,
                                "type": "function",
                            }
                        )
            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)


if __name__ == "__main__":
    root = Path.cwd()
    out_file = root / "artifacts" / "knowledge_graph.json"
    generate_knowledge_graph(root, out_file)
    print(f"Successfully generated knowledge graph to {out_file}")
