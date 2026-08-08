import logging

logger = logging.getLogger(__name__)
import ast
import json
import os
from typing import Any


def generate_knowledge_graph(root_dir: str) -> dict[str, list[dict[str, Any]]]:
    """
    Parses Python files in the repository using `ast` and builds a basic knowledge graph.
    Properly ignores hidden directories.
    """
    knowledge_graph: dict[str, list[dict[str, Any]]] = {
        "files": [],
        "classes": [],
        "functions": [],
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories like .git, .github, .venv
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Ignore specific build artifacts and dependencies
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in [
                "build",
                "node_modules",
                "dist",
                "dist-ssr",
                "venv",
                "__pycache__",
                "artifacts",
            ]
        ]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                knowledge_graph["files"].append(
                    {"path": filepath, "module": filename.replace(".py", "")}
                )

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        knowledge_graph["classes"].append(
                            {
                                "file": filepath,
                                "name": node.name,
                                "docstring": ast.get_docstring(node),
                                "lineno": node.lineno,
                            }
                        )
                    elif isinstance(node, ast.FunctionDef):
                        knowledge_graph["functions"].append(
                            {
                                "file": filepath,
                                "name": node.name,
                                "docstring": ast.get_docstring(node),
                                "lineno": node.lineno,
                            }
                        )

            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to parse {filepath}: {e}")
                continue  # nosec B112

    return knowledge_graph


if __name__ == "__main__":
    kg = generate_knowledge_graph(".")
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(kg, f, indent=2)
    print("Knowledge graph generated at artifacts/knowledge_graph.json")
