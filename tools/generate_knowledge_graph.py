import ast
import json
import os
from typing import Any, Dict, List


def analyze_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            return {"error": str(e)}

    info: Dict[str, List[Dict[str, Any]]] = {"classes": [], "functions": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            info["classes"].append(
                {"name": node.name, "docstring": ast.get_docstring(node)}
            )
        elif isinstance(node, ast.FunctionDef):
            info["functions"].append(
                {"name": node.name, "docstring": ast.get_docstring(node)}
            )

    return info


def main() -> None:
    graph: Dict[str, Any] = {}

    for root, _, files in os.walk("."):
        if (
            ".venv" in root
            or "node_modules" in root
            or ".git" in root
            or "build" in root
            or ".cursor" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                graph[filepath] = analyze_file(filepath)

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print("Knowledge graph generated at artifacts/knowledge_graph.json")


if __name__ == "__main__":
    main()
