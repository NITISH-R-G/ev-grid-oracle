import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def generate_knowledge_graph() -> dict[str, list[dict[str, Any]]]:
    """Generates a simple knowledge graph using AST parsing of Python files."""
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dnames, fnames in os.walk("."):
        # Explicitly bypass hidden directories
        dnames[:] = [d for d in dnames if not d.startswith(".")]

        # Avoid traversing node_modules or large build dirs
        if "node_modules" in root or "dist" in root:
            continue

        for fname in fnames:
            if fname.endswith(".py"):
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source, filename=filepath)

                    file_node: dict[str, Any] = {
                        "id": filepath,
                        "type": "file",
                        "name": fname,
                    }
                    graph["nodes"].append(file_node)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_node = {
                                "id": f"{filepath}::{node.name}",
                                "type": "class",
                                "name": node.name,
                            }
                            graph["nodes"].append(class_node)
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": f"{filepath}::{node.name}",
                                    "type": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            func_node = {
                                "id": f"{filepath}::{node.name}",
                                "type": "function",
                                "name": node.name,
                            }
                            graph["nodes"].append(func_node)
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": f"{filepath}::{node.name}",
                                    "type": "contains",
                                }
                            )
                except Exception:  # noqa: BLE001
                    logger.warning(f"Failed to parse {filepath}")
                    continue

    return graph


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Generating knowledge graph...")

    graph_data = generate_knowledge_graph()

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "knowledge_graph.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2)

    logger.info(f"Knowledge graph written to {out_path}")
