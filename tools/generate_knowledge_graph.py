import ast
import json
import os
from typing import Any


def generate_knowledge_graph(root_dir: str, output_file: str) -> None:
    graph: dict[str, Any] = {"nodes": [], "edges": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories like .git and .venv
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Add file node
                file_id = rel_path
                graph["nodes"].append({"id": file_id, "type": "file", "name": filename})

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_id = f"{file_id}::{node.name}"
                        graph["nodes"].append(
                            {"id": class_id, "type": "class", "name": node.name}
                        )
                        graph["edges"].append(
                            {"source": file_id, "target": class_id, "type": "contains"}
                        )
                    elif isinstance(node, ast.FunctionDef):
                        func_id = f"{file_id}::{node.name}"
                        graph["nodes"].append(
                            {"id": func_id, "type": "function", "name": node.name}
                        )
                        graph["edges"].append(
                            {"source": file_id, "target": func_id, "type": "contains"}
                        )

            except Exception:  # nosec B110  # noqa: BLE001
                pass

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph(".", "artifacts/knowledge_graph.json")
