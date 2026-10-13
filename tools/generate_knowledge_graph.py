import os
import ast
import json
from typing import Any


def extract_knowledge(filepath: str) -> dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return {"classes": [], "functions": [], "imports": []}

    classes = []
    functions = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
                }
            )
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {"classes": classes, "functions": functions, "imports": list(set(imports))}


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(repo_root, "artifacts", "knowledge_graph.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    knowledge_graph: dict[str, Any] = {}

    for root, dnames, fnames in os.walk(repo_root):
        dnames[:] = [d for d in dnames if not d.startswith(".")]
        if any(
            ignored in root
            for ignored in ["venv", "node_modules", "web/dist", "artifacts"]
        ):
            continue

        for fname in fnames:
            if fname.endswith(".py"):
                filepath = os.path.join(root, fname)
                rel_path = os.path.relpath(filepath, repo_root)
                knowledge_graph[rel_path] = extract_knowledge(filepath)

    with open(output_path, "w", encoding="utf-8") as out_f:
        json.dump(knowledge_graph, out_f, indent=2)

    print(f"Knowledge graph generated at {output_path}")


if __name__ == "__main__":
    main()
