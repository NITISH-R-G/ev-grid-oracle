import ast
import json
import os
from typing import Any


def extract_knowledge(filepath: str) -> dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return {"classes": [], "functions": []}

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "lineno": node.lineno,
                }
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            functions.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "lineno": node.lineno,
                }
            )

    return {"classes": classes, "functions": functions}


def main():
    graph: dict[str, Any] = {}

    for root, dirs, files in os.walk("."):
        if ".git" in root or ".venv" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                graph[filepath] = extract_knowledge(filepath)

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    main()
