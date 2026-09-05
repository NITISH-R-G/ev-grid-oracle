import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_architecture_graph() -> dict[str, Any]:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
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
                                    "type": "imports_from",
                                }
                            )
                except Exception:  # noqa: BLE001, S110
                    pass
    return graph


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    graph = generate_architecture_graph()
    output_file = output_dir / "architecture_graph.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.warning(f"Generated architecture diagram at {output_file}")
