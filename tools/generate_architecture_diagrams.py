import ast
import json
import os
from typing import Any


def generate_architecture_diagrams(root_dir: str, output_file: str) -> None:
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
                graph["nodes"].append({"id": file_id, "type": "module"})

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            graph["edges"].append(
                                {
                                    "source": file_id,
                                    "target": alias.name,
                                    "type": "imports",
                                }
                            )
                            if not any(n["id"] == alias.name for n in graph["nodes"]):
                                graph["nodes"].append(
                                    {"id": alias.name, "type": "external_module"}
                                )
                    elif isinstance(node, ast.ImportFrom):
                        module_name = node.module if node.module else "unknown"
                        graph["edges"].append(
                            {
                                "source": file_id,
                                "target": module_name,
                                "type": "imports_from",
                            }
                        )
                        if not any(n["id"] == module_name for n in graph["nodes"]):
                            graph["nodes"].append(
                                {"id": module_name, "type": "external_module"}
                            )

            except Exception:  # nosec B110  # noqa: BLE001
                pass

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams(".", "artifacts/architecture_graph.json")
