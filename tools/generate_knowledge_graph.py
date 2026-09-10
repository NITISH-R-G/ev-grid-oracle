import os
import ast
import json
from typing import Any

def generate_knowledge_graph(root_dir: str) -> dict[str, Any]:
    graph: dict[str, Any] = {"files": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                module = ast.parse(content)
                file_info: dict[str, Any] = {
                    "path": rel_path,
                    "classes": [],
                    "functions": []
                }

                for node in module.body:
                    if isinstance(node, ast.ClassDef):
                        class_info: dict[str, Any] = {
                            "name": node.name,
                            "docstring": ast.get_docstring(node),
                            "methods": []
                        }
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                class_info["methods"].append({
                                    "name": item.name,
                                    "docstring": ast.get_docstring(item)
                                })
                        file_info["classes"].append(class_info)
                    elif isinstance(node, ast.FunctionDef):
                        file_info["functions"].append({
                            "name": node.name,
                            "docstring": ast.get_docstring(node)
                        })

                graph["files"].append(file_info)
            except Exception as e: # noqa: BLE001
                pass

    return graph

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    kg = generate_knowledge_graph(root)

    out_dir = os.path.join(root, 'artifacts')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'knowledge_graph.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(kg, f, indent=2)
    print(f"Generated knowledge graph at {out_path}")
