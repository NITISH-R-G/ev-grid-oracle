import ast
import json
import os
from typing import Any


def parse_file(filepath: str) -> list[dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    nodes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            nodes.append({"type": "class", "name": node.name, "file": filepath})
        elif isinstance(node, ast.FunctionDef):
            nodes.append({"type": "function", "name": node.name, "file": filepath})

    return nodes


def generate_knowledge_graph() -> None:
    graph: list[dict[str, Any]] = []
    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in [
                "venv",
                "node_modules",
                "dashboard_output",
                "artifacts",
                "docs",
                "web",
            ]
        ]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                graph.extend(parse_file(filepath))

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
