import os
import ast
import json


def parse_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception:
            return None

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)

    return {"classes": classes, "functions": functions}


def build_graph():
    graph = {}
    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                info = parse_file(filepath)
                if info and (info["classes"] or info["functions"]):
                    graph[filepath] = info

    with open("knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    build_graph()
