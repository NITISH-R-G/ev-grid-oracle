import ast
import json
import os
from typing import Any


def generate_architecture_diagrams() -> None:
    graph_data: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "venv" in dirs:
            dirs.remove("venv")
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, ".")

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=rel_path)

                    graph_data["nodes"].append(
                        {"id": rel_path, "type": "file", "label": file}
                    )

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                target = alias.name
                                graph_data["edges"].append(
                                    {
                                        "source": rel_path,
                                        "target": target,
                                        "type": "imports",
                                    }
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                target = node.module
                                graph_data["edges"].append(
                                    {
                                        "source": rel_path,
                                        "target": target,
                                        "type": "imports_from",
                                    }
                                )
                except Exception:
                    pass  # nosec B110

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams()
