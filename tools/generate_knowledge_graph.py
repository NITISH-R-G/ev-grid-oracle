import os
import json
import ast
from typing import Any


def generate_knowledge_graph():
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        # Explicitly skip hidden directories, node_modules, etc.
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ["node_modules", "artifacts", "docs", "venv", "__pycache__"]
        ]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                node_id = filepath.replace("./", "")

                graph["nodes"].append({"id": node_id, "type": "file", "name": file})

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_id = f"{node_id}::{node.name}"
                            graph["nodes"].append(
                                {"id": class_id, "type": "class", "name": node.name}
                            )
                            graph["edges"].append(
                                {
                                    "source": node_id,
                                    "target": class_id,
                                    "relation": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef) or isinstance(
                            node, ast.AsyncFunctionDef
                        ):
                            func_id = f"{node_id}::{node.name}"
                            graph["nodes"].append(
                                {"id": func_id, "type": "function", "name": node.name}
                            )
                            graph["edges"].append(
                                {
                                    "source": node_id,
                                    "target": func_id,
                                    "relation": "contains",
                                }
                            )
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
