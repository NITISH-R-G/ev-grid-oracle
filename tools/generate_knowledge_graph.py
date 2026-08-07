import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def generate_graph() -> None:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk("."):
        if not root.startswith("."):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    graph["nodes"].append({"id": path, "type": "file"})
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read(), filename=path)
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    node_id = f"{path}::{node.name}"
                                    graph["nodes"].append(
                                        {
                                            "id": node_id,
                                            "type": "class",
                                            "name": node.name,
                                        }
                                    )
                                    graph["edges"].append(
                                        {
                                            "source": path,
                                            "target": node_id,
                                            "type": "contains",
                                        }
                                    )
                                elif isinstance(node, ast.FunctionDef):
                                    node_id = f"{path}::{node.name}"
                                    graph["nodes"].append(
                                        {
                                            "id": node_id,
                                            "type": "function",
                                            "name": node.name,
                                        }
                                    )
                                    graph["edges"].append(
                                        {
                                            "source": path,
                                            "target": node_id,
                                            "type": "contains",
                                        }
                                    )
                    except Exception as e:
                        logger.warning("Error parsing %s: %s", path, e)
    with open("knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_graph()
