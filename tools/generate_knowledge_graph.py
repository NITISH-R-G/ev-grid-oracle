import ast
import os
import json
from typing import Dict, List, Any


def generate_knowledge_graph(repo_path: str) -> Dict[str, Any]:
    graph: Dict[str, Any] = {"files": {}, "modules": {}, "classes": {}, "functions": {}}

    for root, _, files in os.walk(repo_path):
        if (
            "venv" in root
            or ".venv" in root
            or "node_modules" in root
            or ".git" in root
            or "__pycache__" in root
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    classes: List[str] = []
                    functions: List[str] = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes.append(node.name)
                            graph["classes"][node.name] = {
                                "file": filepath,
                                "docstring": ast.get_docstring(node),
                            }
                        elif isinstance(node, ast.FunctionDef) or isinstance(
                            node, ast.AsyncFunctionDef
                        ):
                            functions.append(node.name)
                            graph["functions"][node.name] = {
                                "file": filepath,
                                "docstring": ast.get_docstring(node),
                            }

                    graph["files"][filepath] = {
                        "classes": classes,
                        "functions": functions,
                    }
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")

    return graph


if __name__ == "__main__":
    repo_path = "."
    graph = generate_knowledge_graph(repo_path)

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print("Knowledge graph generated at artifacts/knowledge_graph.json")
