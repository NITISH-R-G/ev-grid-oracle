import ast
import json
import os
from typing import Any


def generate_knowledge_graph() -> dict[str, list[dict[str, Any]]]:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": []}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            graph["nodes"].append(
                                {
                                    "id": f"{filepath}:{node.name}",
                                    "type": "class",
                                    "file": filepath,
                                    "name": node.name,
                                    "doc": ast.get_docstring(node),
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            graph["nodes"].append(
                                {
                                    "id": f"{filepath}:{node.name}",
                                    "type": "function",
                                    "file": filepath,
                                    "name": node.name,
                                    "doc": ast.get_docstring(node),
                                }
                            )
                except Exception:  # nosec B110
                    pass  # noqa: BLE001

    return graph


if __name__ == "__main__":
    import os

    os.makedirs("artifacts", exist_ok=True)
    graph = generate_knowledge_graph()
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print("Knowledge graph generated at artifacts/knowledge_graph.json")
