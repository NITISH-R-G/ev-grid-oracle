import ast
import json
import os
from typing import Any


def generate_architecture_graph() -> None:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in [
                "venv",
                "node_modules",
                "dashboard_output",
                "artifacts",
                "docs",
                "web",
            ]
        ]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                graph["nodes"].append({"id": filepath, "label": file})

                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            graph["edges"].append(
                                {"source": filepath, "target": alias.name}
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            graph["edges"].append(
                                {"source": filepath, "target": node.module}
                            )

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture_graph()
