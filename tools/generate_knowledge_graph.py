import ast
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_knowledge_graph(
    source_dir: str = ".", output_file: str = "artifacts/knowledge_graph.json"
) -> None:
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    graph: dict[str, Any] = {
        "files": [],
        "classes": [],
        "functions": [],
        "relationships": [],
    }

    for root, dirs, files in os.walk(source_dir):
        # Explicitly skip ignored directories
        if any(
            ignored in root.split(os.path.sep)
            for ignored in [".git", ".venv", "__pycache__", "node_modules", ".cursor"]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)
                graph["files"].append({"path": rel_path})

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()

                    tree = ast.parse(source_code)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            graph["classes"].append(
                                {
                                    "name": node.name,
                                    "file": rel_path,
                                    "docstring": docstring,
                                }
                            )
                            graph["relationships"].append(
                                {
                                    "source": rel_path,
                                    "target": node.name,
                                    "type": "contains_class",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            graph["functions"].append(
                                {
                                    "name": node.name,
                                    "file": rel_path,
                                    "docstring": docstring,
                                }
                            )
                            graph["relationships"].append(
                                {
                                    "source": rel_path,
                                    "target": node.name,
                                    "type": "contains_function",
                                }
                            )
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")

    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(graph, out, indent=2)

    logger.info(f"Knowledge graph generated at {output_file}")


if __name__ == "__main__":
    generate_knowledge_graph()
