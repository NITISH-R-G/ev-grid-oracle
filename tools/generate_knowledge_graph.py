import ast
import os
import json
import logging
from typing import Any, Dict


def generate_graph() -> None:
    graph: Dict[str, list[Dict[str, Any]]] = {"nodes": [], "edges": []}
    for root, _, files in os.walk("."):
        if "venv" in root or ".git" in root or ".venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                graph["nodes"].append({"id": path, "type": "file"})
                try:
                    with open(path, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            graph["nodes"].append({"id": node.name, "type": "class"})
                            graph["edges"].append(
                                {
                                    "source": path,
                                    "target": node.name,
                                    "type": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            graph["nodes"].append({"id": node.name, "type": "function"})
                            graph["edges"].append(
                                {
                                    "source": path,
                                    "target": node.name,
                                    "type": "contains",
                                }
                            )
                except Exception as e:
                    logging.warning(f"Error parsing {path}: {e}")
    with open("knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_graph()
