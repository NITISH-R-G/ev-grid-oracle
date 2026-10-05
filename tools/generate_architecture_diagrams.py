import ast
import json
import os
from typing import Any


def generate_architecture_diagrams() -> dict[str, Any]:
    graph: dict[str, Any] = {"nodes": [], "edges": []}
    modules: dict[str, str] = {}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                module_name = file.replace(".py", "")
                modules[module_name] = filepath
                graph["nodes"].append({"id": module_name, "type": "module"})

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                module_name = file.replace(".py", "")
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name in modules:
                                    graph["edges"].append(
                                        {"source": module_name, "target": alias.name}
                                    )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module and node.module in modules:
                                graph["edges"].append(
                                    {"source": module_name, "target": node.module}
                                )
                except Exception:  # nosec B110
                    pass  # noqa: BLE001

    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = generate_architecture_diagrams()
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print("Architecture diagram generated at artifacts/architecture_graph.json")
