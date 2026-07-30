#!/usr/bin/env python3
"""
Generates a JSON knowledge graph of the repository based on AST parsing.
"""

import ast
import json
import os
from typing import Any


def parse_file(filepath: str) -> dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception as e:
        return {"error": str(e)}

    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []

    # Safely get module docstring
    module_doc = ast.get_docstring(tree) or ""

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node) or ""
            methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
            classes.append({"name": node.name, "doc": class_doc, "methods": methods})
        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node) or ""
            functions.append({"name": node.name, "doc": func_doc})

    return {"classes": classes, "functions": functions, "doc": module_doc}


def main() -> None:
    graph: dict[str, dict[str, Any]] = {}

    # Directories to scan
    scan_dirs = ["ev_grid_oracle", "server", "tools", "viz", "training"]

    for d in scan_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    graph[filepath] = parse_file(filepath)

    os.makedirs("docs", exist_ok=True)
    out_path = os.path.join("docs", "knowledge_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Generated {out_path}")


if __name__ == "__main__":
    main()
