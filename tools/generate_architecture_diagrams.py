#!/usr/bin/env python3
"""
Autonomous Architecture Graph Generator.
Parses Python files using the `ast` module to build a dependency graph
of imports, and outputs it to `artifacts/architecture_graph.json`.
"""

import ast
import json
import os
import sys


def build_architecture_graph(repo_root: str):
    graph: dict[str, list[str]] = {}

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

            deps = []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        deps.append(alias.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    deps.append(node.module)

            graph[rel_path] = list(set(deps))

    artifacts_dir = os.path.join(repo_root, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)
    out_path = os.path.join(artifacts_dir, "architecture_graph.json")

    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump(graph, out_f, indent=2)


if __name__ == "__main__":
    build_architecture_graph(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    )
