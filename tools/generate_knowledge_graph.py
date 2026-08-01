"""
Autonomous Knowledge Graph Generator.

This tool statically analyzes the repository to build a knowledge graph of
files, classes, and functions to enable natural-language discovery of repository knowledge.
"""

import ast
import json
import os
import sys
from typing import Any


def parse_file(filepath: str) -> dict[str, list[dict[str, Any]]]:
    """Parse a python file and extract classes and functions."""
    result: dict[str, list[dict[str, Any]]] = {"classes": [], "functions": []}
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read {filepath}: {e}", file=sys.stderr)
        return result

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return result

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [
                n.name
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            result["classes"].append(
                {
                    "name": node.name,
                    "methods": methods,
                    "docstring": ast.get_docstring(node),
                }
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Only add top-level functions (crude check, but fine for now)
            result["functions"].append(
                {"name": node.name, "docstring": ast.get_docstring(node)}
            )

    return result


def main() -> None:
    """Main execution."""
    knowledge_graph: dict[str, Any] = {"files": {}}

    # Exclude directories
    exclude_dirs = {
        "venv",
        "__pycache__",
        "node_modules",
        "dashboard_output",
    }

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                # Normalize path
                filepath = os.path.normpath(filepath)
                knowledge_graph["files"][filepath] = parse_file(filepath)

    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "knowledge_graph.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=2)

    print(f"Successfully generated knowledge graph at {output_path}")


if __name__ == "__main__":
    main()
