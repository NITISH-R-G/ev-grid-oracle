import ast
import json
import logging
import os
from typing import Any


def extract_info(filepath: str) -> dict[str, Any]:
    """Extract classes and functions from a python file."""
    info: dict[str, list[dict[str, Any]]] = {"classes": [], "functions": []}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                methods = []
                for child in node.body:
                    if isinstance(child, ast.FunctionDef):
                        methods.append(child.name)
                info["classes"].append({"name": node.name, "methods": methods})

            elif isinstance(node, ast.FunctionDef):
                info["functions"].append({"name": node.name})

    except Exception as e:
        logging.getLogger(__name__).warning(f"Error: {e}")

    return info

def main() -> None:
    """Generate knowledge graph from source files."""
    graph: dict[str, Any] = {"files": {}}

    directories_to_scan = ["server", "ev_grid_oracle", "tools"]

    for dir_name in directories_to_scan:
        if not os.path.exists(dir_name):
            continue

        for root, dirs, files in os.walk(dir_name):
            if not root.startswith('.'):
                for file in files:
                    if file.endswith(".py"):
                        filepath = os.path.join(root, file)
                        graph["files"][filepath] = extract_info(filepath)

    output_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "knowledge_graph.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Knowledge graph generated at {out_path}")

if __name__ == "__main__":
    main()
