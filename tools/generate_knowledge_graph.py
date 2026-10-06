import os
import ast
import json
from typing import Any


def generate_knowledge_graph(root_dir: str, output_file: str) -> None:
    graph: dict[str, dict[str, list[dict[str, Any]]]] = {"files": {}}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
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
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            functions.append(
                                {
                                    "name": node.name,
                                    "docstring": ast.get_docstring(node),
                                }
                            )

                    graph["files"][rel_path] = {
                        "classes": classes,
                        "functions": functions,
                    }
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph(".", "artifacts/knowledge_graph.json")
