import ast
import os
import json
from typing import Any


def generate_knowledge_graph() -> None:
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

                # File node
                graph["nodes"].append({"id": filepath, "type": "file"})

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    for node in tree.body:
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

                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    out_path = os.path.join(artifacts_dir, "knowledge_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
