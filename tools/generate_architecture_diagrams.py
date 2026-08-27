import os
import ast
import json
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_architecture_diagrams() -> None:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    modules = set()

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                modules.add(filepath)
                graph["nodes"].append({"id": filepath, "type": "module"})

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

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
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                graph["edges"].append(
                                    {
                                        "source": filepath,
                                        "target": node.module,
                                        "type": "imports_from",
                                    }
                                )
                except Exception as e:
                    logger.warning(f"Failed to parse imports in {filepath}: {e}")

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as out:
        json.dump(graph, out, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams()
