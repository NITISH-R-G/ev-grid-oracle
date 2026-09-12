import os
import json
import ast
from typing import Any


def generate_architecture():
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    # Store imported modules per file
    imports_map = {}

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ["node_modules", "artifacts", "docs", "venv", "__pycache__"]
        ]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                module_name = (
                    filepath.replace("./", "").replace("/", ".").replace(".py", "")
                )

                graph["nodes"].append(
                    {"id": module_name, "type": "module", "name": file}
                )

                imported_modules = []
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imported_modules.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imported_modules.append(node.module)

                    imports_map[module_name] = imported_modules
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")

    for module, imports in imports_map.items():
        for imp in imports:
            graph["edges"].append(
                {"source": module, "target": imp, "relation": "imports"}
            )
            # Ensure target node exists
            if not any(n["id"] == imp for n in graph["nodes"]):
                graph["nodes"].append(
                    {"id": imp, "type": "external_module", "name": imp}
                )

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture()
