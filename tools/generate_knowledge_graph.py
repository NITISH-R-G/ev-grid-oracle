#!/usr/bin/env python3
"""
Autonomous Knowledge Graph Generator
Parses repository Python files and builds a knowledge graph representing files,
classes, and functions using the ast module.
"""

import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_knowledge_graph(root_dir: str = ".") -> dict[str, Any]:
    graph: dict[str, Any] = {"files": {}, "classes": {}, "functions": {}}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Explicitly ignore hidden directories (like .git, .github) and common excludes
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".") and d not in ("venv", "node_modules", "artifacts")
        ]

        for file in filenames:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue  # nosec B112

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            file_info: dict[str, Any] = {
                "classes": [],
                "functions": [],
                "path": filepath,
            }
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info: dict[str, Any] = {
                        "name": node.name,
                        "methods": [],
                        "docstring": ast.get_docstring(node),
                    }
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info["methods"].append(item.name)  # type: ignore
                    graph["classes"][node.name] = class_info
                    file_info["classes"].append(node.name)  # type: ignore
                elif isinstance(node, ast.FunctionDef):
                    # Only grab top-level functions (ignoring methods handled above by simple traversal logic)
                    func_info: dict[str, Any] = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                    }
                    graph["functions"][node.name] = func_info
                    file_info["functions"].append(node.name)  # type: ignore

            graph["files"][filepath] = file_info

    return graph


def main() -> None:
    root_dir = Path(__file__).parent.parent
    graph = generate_knowledge_graph(str(root_dir))

    out_dir = root_dir / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "knowledge_graph.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph written to {out_file}")


if __name__ == "__main__":
    main()
