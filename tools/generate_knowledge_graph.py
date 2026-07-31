import ast
import os
import json


def extract_info(filepath):
    with open(filepath, "r") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return None

    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]

    return {"file": filepath, "classes": classes, "functions": functions}


def main():
    graph = []
    for root, _, files in os.walk("."):
        if ".venv" in root or "node_modules" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                info = extract_info(filepath)
                if info:
                    graph.append(info)

    os.makedirs("docs", exist_ok=True)
    with open("docs/knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    main()
