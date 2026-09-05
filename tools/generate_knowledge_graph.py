import ast
import json
import os
from typing import Any


def generate_knowledge_graph() -> None:
    """Generates a JSON knowledge graph of Python files in the repository."""
    graph: dict[str, dict[str, list[dict[str, Any]]]] = {}

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in [
                "venv",
                "env",
                "__pycache__",
                "node_modules",
                "dashboard_output",
                "build",
                "dist",
            ]
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    classes = []
                    functions = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes.append(
                                {
                                    "name": node.name,
                                    "docstring": ast.get_docstring(node),
                                    "line_number": node.lineno,
                                }
                            )
                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            functions.append(
                                {
                                    "name": node.name,
                                    "docstring": ast.get_docstring(node),
                                    "line_number": node.lineno,
                                }
                            )

                    if classes or functions:
                        graph[file_path] = {"classes": classes, "functions": functions}
                except Exception as e:  # noqa: BLE001
                    print(f"Error parsing {file_path}: {e}")

    with open("knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print("Generated knowledge_graph.json successfully.")


if __name__ == "__main__":
    generate_knowledge_graph()
