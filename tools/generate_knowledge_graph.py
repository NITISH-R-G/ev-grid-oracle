#!/usr/bin/env python3
"""
Autonomous Knowledge Graph Generator.
Parses Python files to build a structural representation of the repository,
including files, classes, and functions, and outputs it to an artifacts JSON file.
"""

import ast
import json
import os
import sys
from typing import Any


def build_knowledge_graph(repo_root: str):
    graph: dict[str, Any] = {"files": []}

    for root_dir, dirs, files in os.walk(repo_root):
        if (
            ".git" in root_dir
            or "node_modules" in root_dir
            or ".venv" in root_dir
            or "venv" in root_dir
        ):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root_dir, file)
            rel_path = os.path.relpath(filepath, repo_root)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=filepath)
            except Exception as e:  # noqa: BLE001
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

            file_info: dict[str, Any] = {
                "path": rel_path,
                "classes": [],
                "functions": [],
            }

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "methods": [
                            n.name for n in node.body if isinstance(n, ast.FunctionDef)
                        ],
                    }
                    file_info["classes"].append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    file_info["functions"].append(node.name)

            graph["files"].append(file_info)

    artifacts_dir = os.path.join(repo_root, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    out_path = os.path.join(artifacts_dir, "knowledge_graph.json")

    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump(graph, out_f, indent=2)


if __name__ == "__main__":
    build_knowledge_graph(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )
