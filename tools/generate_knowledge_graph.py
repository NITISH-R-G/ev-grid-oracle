import os
import ast
import json
from typing import Dict, List, Any


def generate_knowledge_graph(repo_path: str = ".") -> Dict[str, List[Dict[str, Any]]]:
    graph: Dict[str, List[Dict[str, Any]]] = {
        "files": [],
        "classes": [],
        "functions": [],
    }

    for root, dirs, files in os.walk(repo_path):
        if any(
            ignored in root
            for ignored in [
                ".venv",
                "venv",
                ".git",
                "node_modules",
                "artifacts",
                "dashboard_output",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content)

                    file_info: Dict[str, Any] = {
                        "path": filepath,
                        "name": file,
                        "classes": [],
                        "functions": [],
                    }

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_info = {
                                "name": node.name,
                                "file": filepath,
                                "line": node.lineno,
                                "docstring": ast.get_docstring(node),
                            }
                            graph["classes"].append(class_info)
                            file_info["classes"].append(node.name)

                        elif isinstance(node, ast.FunctionDef):
                            func_info = {
                                "name": node.name,
                                "file": filepath,
                                "line": node.lineno,
                                "docstring": ast.get_docstring(node),
                            }
                            graph["functions"].append(func_info)
                            file_info["functions"].append(node.name)

                    graph["files"].append(file_info)

                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    return graph


if __name__ == "__main__":
    kg = generate_knowledge_graph()

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(kg, f, indent=2)
    print("Knowledge graph generated at artifacts/knowledge_graph.json")
