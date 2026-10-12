import ast
import json
import os
import pathlib
from typing import Any


def extract_knowledge(filepath: str) -> dict[str, list[dict[str, Any]]]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
    except Exception:
        return {"classes": [], "functions": []}

    knowledge: dict[str, list[dict[str, Any]]] = {"classes": [], "functions": []}

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            knowledge["classes"].append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "methods": [
                        n.name for n in node.body if isinstance(n, ast.FunctionDef)
                    ],
                }
            )
        elif isinstance(node, ast.FunctionDef):
            knowledge["functions"].append(
                {"name": node.name, "docstring": ast.get_docstring(node)}
            )

    return knowledge


def generate_graph():
    root = pathlib.Path(".")
    out_dir = pathlib.Path("artifacts")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "knowledge_graph.json"

    graph = {}

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        if "node_modules" in dirpath or "dist" in dirpath or "venv" in dirpath:
            continue

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)

                module_name = filepath.replace("/", ".").replace(".py", "")
                module_name = module_name.lstrip(".")

                graph[module_name] = extract_knowledge(filepath)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_graph()
    print("Knowledge graph generated.")
