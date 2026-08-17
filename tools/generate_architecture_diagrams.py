import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)


def build_dependency_graph(root_dir="."):
    graph = {}
    for dirpath, _, filenames in os.walk(root_dir):
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
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append(node.module)
                    graph[filepath] = imports
                except Exception as e:
                    logging.warning(f"Failed to parse {filepath}: {e}")
    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = build_dependency_graph()
    with open("artifacts/architecture_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    logging.info(
        "Architecture dependency graph generated at artifacts/architecture_graph.json"
    )
