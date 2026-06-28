import os
import ast
import json
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)


def generate_knowledge_graph(directory: str = ".") -> None:
    graph: Dict[str, List[Dict[str, str]]] = {"nodes": [], "edges": []}

    # Simple extraction of classes and functions
    for root, _, files in os.walk(directory):
        if (
            "venv" in root
            or ".venv" in root
            or "node_modules" in root
            or ".git" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                graph["nodes"].append(
                                    {
                                        "id": node.name,
                                        "type": "class",
                                        "file": filepath,
                                    }
                                )
                            elif isinstance(node, ast.FunctionDef):
                                graph["nodes"].append(
                                    {
                                        "id": node.name,
                                        "type": "function",
                                        "file": filepath,
                                    }
                                )
                except Exception as e:
                    logging.warning(f"Failed to parse {filepath}: {e}")

    os.makedirs("docs/knowledge", exist_ok=True)
    with open("docs/knowledge/graph.json", "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
