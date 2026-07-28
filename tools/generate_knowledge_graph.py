import ast
import json
import os
from typing import Any


def parse_file(filepath: str) -> dict[str, Any]:
    with open(filepath, encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception:
        return {}

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "docstring": ast.get_docstring(node)})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append({"name": node.name, "docstring": ast.get_docstring(node)})

    return {"filepath": filepath, "classes": classes, "functions": functions}


def main() -> None:
    knowledge_graph: dict[str, list[dict[str, Any]]] = {"files": []}

    for root, _, files in os.walk("."):
        if (
            ".venv" in root
            or "venv" in root
            or "node_modules" in root
            or ".git" in root
            or ".cursor" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                parsed_info = parse_file(filepath)
                if parsed_info:
                    knowledge_graph["files"].append(parsed_info)

    os.makedirs("docs", exist_ok=True)
    with open("docs/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=4)


if __name__ == "__main__":
    main()
