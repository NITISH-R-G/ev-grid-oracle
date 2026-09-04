import ast
import json
import os
from typing import Any


def generate_knowledge_graph() -> None:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk("."):
        if ".git" in root or ".venv" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                    graph["nodes"].append({"id": filepath, "type": "file"})
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_id = f"{filepath}::{node.name}"
                            graph["nodes"].append({"id": class_id, "type": "class"})
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": class_id,
                                    "type": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            func_id = f"{filepath}::{node.name}"
                            graph["nodes"].append({"id": func_id, "type": "function"})
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": func_id,
                                    "type": "contains",
                                }
                            )
                except Exception:  # noqa: BLE001, S110
                    pass

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
