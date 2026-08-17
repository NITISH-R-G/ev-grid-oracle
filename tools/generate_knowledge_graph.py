import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)


def extract_info(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        classes = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        return {"classes": classes, "functions": functions}
    except Exception as e:
        logging.warning(f"Failed to parse {filepath}: {e}")
        return {}


def build_graph(root_dir="."):
    graph = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if any(
            d in dirpath
            for d in [
                ".git",
                "__pycache__",
                ".venv",
                "node_modules",
                "venv",
                "artifacts",
                "docs",
            ]
        ):
            continue
        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                graph[filepath] = extract_info(filepath)
    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = build_graph()
    with open("artifacts/knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    logging.info("Knowledge graph generated at artifacts/knowledge_graph.json")
