import ast
import json
import os
from typing import Any, Dict


def parse_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            return {"error": str(e)}

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return {"classes": classes, "functions": functions}


def generate_knowledge_graph(root_dir: str = ".") -> Dict[str, Dict[str, Any]]:
    graph: Dict[str, Dict[str, Any]] = {}
    for subdir, _, files in os.walk(root_dir):
        if ".venv" in subdir or "node_modules" in subdir or "__pycache__" in subdir:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(subdir, file)
                graph[filepath] = parse_file(filepath)

    return graph


if __name__ == "__main__":
    kg = generate_knowledge_graph()
    with open("knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(kg, f, indent=2)
    print("Knowledge graph generated successfully at knowledge_graph.json")
