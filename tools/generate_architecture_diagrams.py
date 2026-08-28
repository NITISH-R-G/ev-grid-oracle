import os
import ast
import json
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_architecture_diagrams(source_dir: str = ".", output_file: str = "artifacts/architecture_graph.json") -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Store relationships as dependencies (e.g., file -> imported module)
    graph: dict[str, Any] = {
        "nodes": [],
        "links": []
    }

    nodes_set = set()

    for root, dirs, files in os.walk(source_dir):
        # Explicitly skip ignored directories
        if any(ignored in root.split(os.path.sep) for ignored in [".git", ".venv", "__pycache__", "node_modules", ".cursor"]):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                module_name = rel_path.replace(os.path.sep, ".").replace(".py", "")
                nodes_set.add(module_name)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()

                    tree = ast.parse(source_code)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["links"].append({
                                    "source": module_name,
                                    "target": alias.name,
                                    "type": "imports"
                                })
                                nodes_set.add(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                graph["links"].append({
                                    "source": module_name,
                                    "target": node.module,
                                    "type": "imports_from"
                                })
                                nodes_set.add(node.module)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}") # noqa: BLE001

    for node in nodes_set:
        graph["nodes"].append({"id": node})

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(graph, out, indent=2)

    logger.info(f"Architecture diagram graph generated at {output_file}")

if __name__ == "__main__":
    generate_architecture_diagrams()
