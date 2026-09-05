import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_knowledge_graph() -> dict[str, Any]:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    graph["nodes"].append(
                        {"id": filepath, "type": "file", "name": file}
                    )

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_id = f"{filepath}::{node.name}"
                            graph["nodes"].append(
                                {"id": class_id, "type": "class", "name": node.name}
                            )
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": class_id,
                                    "type": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            func_id = f"{filepath}::{node.name}"
                            graph["nodes"].append(
                                {"id": func_id, "type": "function", "name": node.name}
                            )
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": func_id,
                                    "type": "contains",
                                }
                            )

                except Exception:  # noqa: BLE001, S110
                    # Catch and ignore parsing errors for basic implementation
                    pass
    return graph


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    graph = generate_knowledge_graph()
    output_file = output_dir / "knowledge_graph.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.warning(f"Generated knowledge graph at {output_file}")
