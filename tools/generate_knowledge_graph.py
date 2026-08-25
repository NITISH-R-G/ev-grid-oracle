import ast
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_knowledge_graph(repo_root: str, output_path: str) -> None:
    graph: dict[str, Any] = {"files": {}, "classes": {}, "functions": {}}

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_root)

                graph["files"][rel_path] = {"classes": [], "functions": []}

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            graph["files"][rel_path]["classes"].append(node.name)
                            graph["classes"][f"{rel_path}:{node.name}"] = {
                                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                            }
                        elif isinstance(node, ast.FunctionDef):
                            graph["files"][rel_path]["functions"].append(node.name)
                            graph["functions"][f"{rel_path}:{node.name}"] = {}

                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    generate_knowledge_graph('.', 'artifacts/knowledge_graph.json')