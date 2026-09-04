import ast
import json
import os
from typing import Any


def generate_architecture_diagrams() -> None:
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
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["edges"].append(
                                    {
                                        "source": filepath,
                                        "target": alias.name,
                                        "type": "imports",
                                    }
                                )
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": node.module,
                                    "type": "imports",
                                }
                            )
                except Exception:  # noqa: BLE001, S110
                    pass

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams()
