import ast
import json
import os
from typing import Any


def generate_knowledge_graph() -> None:
    knowledge_graph: dict[str, Any] = {
        "files": [],
        "classes": [],
        "functions": [],
    }

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # also ignore some other obvious non-source directories
        dirs[:] = [
            d for d in dirs if d not in ("node_modules", "artifacts", "web", "docs")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue  # nosec B112

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            file_info: dict[str, Any] = {
                "filepath": filepath,
                "classes": [],
                "functions": [],
            }

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "filepath": filepath,
                    }
                    knowledge_graph["classes"].append(class_info)
                    file_info["classes"].append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_info = {
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "filepath": filepath,
                    }
                    knowledge_graph["functions"].append(func_info)
                    file_info["functions"].append(node.name)

            knowledge_graph["files"].append(file_info)

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
