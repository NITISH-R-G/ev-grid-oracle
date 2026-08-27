import ast
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_knowledge_graph() -> None:
    graph: dict[str, list[Any]] = {
        "files": [],
        "classes": [],
        "functions": [],
        "relationships": [],
    }

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)
                    graph["files"].append(filepath)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            graph["classes"].append(
                                {
                                    "name": node.name,
                                    "file": filepath,
                                    "docstring": docstring,
                                }
                            )
                            graph["relationships"].append(
                                {
                                    "source": filepath,
                                    "target": node.name,
                                    "type": "contains_class",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            graph["functions"].append(
                                {
                                    "name": node.name,
                                    "file": filepath,
                                    "docstring": docstring,
                                }
                            )
                            graph["relationships"].append(
                                {
                                    "source": filepath,
                                    "target": node.name,
                                    "type": "contains_function",
                                }
                            )
                except Exception as e:
                    logger.warning(f"Failed to parse {filepath}: {e}")

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as out:
        json.dump(graph, out, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
