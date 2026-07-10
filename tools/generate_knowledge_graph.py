import ast
import json
import os
from typing import Any, Dict


def parse_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content, filename=filepath)
        except Exception as e:
            return {"error": str(e)}

    classes = []
    functions = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                }
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            functions.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                }
            )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {
        "classes": classes,
        "functions": functions,
        "imports": list(set(imports)),
    }


def generate_knowledge_graph(root_dir: str) -> Dict[str, Any]:
    graph: Dict[str, Any] = {"files": {}}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude common directories
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in [
                ".git",
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                "build",
                "dist",
            ]
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                graph["files"][rel_path] = parse_file(filepath)

    return graph


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    knowledge_graph = generate_knowledge_graph(root)
    output_path = os.path.join(root, "artifacts", "knowledge_graph.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=2)
    print(f"Knowledge graph generated at {output_path}")
