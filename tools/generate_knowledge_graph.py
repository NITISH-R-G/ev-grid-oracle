import os
import ast
import json
from typing import Dict, List, Any


def parse_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception:
        return {}

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "docstring": ast.get_docstring(node)})
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            functions.append({"name": node.name, "docstring": ast.get_docstring(node)})

    return {"filepath": filepath, "classes": classes, "functions": functions}


def main() -> None:
    knowledge_graph: Dict[str, List[Dict[str, Any]]] = {"files": []}

    for root, _, files in os.walk("."):
        if (
            ".venv" in root
            or "venv" in root
            or "node_modules" in root
            or ".git" in root
            or ".cursor" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                parsed_info = parse_file(filepath)
                if parsed_info:
                    knowledge_graph["files"].append(parsed_info)

    os.makedirs("docs", exist_ok=True)
    with open("docs/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=4)


if __name__ == "__main__":
    main()
