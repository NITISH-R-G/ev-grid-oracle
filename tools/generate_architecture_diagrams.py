import ast
import os
import json
from typing import Any


def generate_architecture_diagram() -> None:
    artifacts_dir = "artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)

    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                module_name = (
                    filepath.replace("/", ".").replace("\\", ".").replace(".py", "")
                )

                # File node
                graph["nodes"].append({"id": module_name, "type": "module"})

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    for node in tree.body:
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["edges"].append(
                                    {
                                        "source": module_name,
                                        "target": alias.name,
                                        "type": "imports",
                                    }
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                graph["edges"].append(
                                    {
                                        "source": module_name,
                                        "target": node.module,
                                        "type": "imports_from",
                                    }
                                )

                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    out_path = os.path.join(artifacts_dir, "architecture_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagram()
