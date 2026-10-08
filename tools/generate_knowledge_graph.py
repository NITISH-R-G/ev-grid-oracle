import ast
import json
import os
from typing import Any


def generate_knowledge_graph(root_dir: str = ".") -> None:
    graph: dict[str, list[Any]] = {
        "files": [],
        "functions": [],
        "classes": [],
        "dependencies": [],
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden system directories to robustly bypass .git, .github, etc.
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        # Also ignore some common environments/artifacts
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in ("node_modules", "venv", "dashboard_output", "artifacts", "docs")
        ]

        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                graph["files"].append(filepath)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            graph["functions"].append(
                                {
                                    "name": node.name,
                                    "file": filepath,
                                    "line": node.lineno,
                                }
                            )
                        elif isinstance(node, ast.ClassDef):
                            graph["classes"].append(
                                {
                                    "name": node.name,
                                    "file": filepath,
                                    "line": node.lineno,
                                }
                            )
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["dependencies"].append(
                                    {"module": alias.name, "file": filepath}
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                graph["dependencies"].append(
                                    {"module": node.module, "file": filepath}
                                )
                except Exception:  # nosec B110
                    pass

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
