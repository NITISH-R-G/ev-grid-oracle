import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_graph() -> None:
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    graph: dict[str, Any] = {"files": [], "classes": [], "functions": [], "edges": []}

    root_dir = Path(".")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories (e.g. .git, .github, .venv)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Ignore common build/test directories
        if any(
            ignored in dirpath
            for ignored in [
                "node_modules",
                "__pycache__",
                "dist",
                "build",
                "artifacts",
                "docs",
            ]
        ):
            continue

        for file in filenames:
            if file.endswith(".py"):
                file_path = Path(dirpath) / file
                graph["files"].append(str(file_path))

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            graph["classes"].append(
                                {"name": node.name, "file": str(file_path)}
                            )
                            graph["edges"].append(
                                {
                                    "source": str(file_path),
                                    "target": node.name,
                                    "type": "contains",
                                }
                            )
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    graph["functions"].append(
                                        {
                                            "name": item.name,
                                            "class": node.name,
                                            "file": str(file_path),
                                        }
                                    )
                                    graph["edges"].append(
                                        {
                                            "source": node.name,
                                            "target": item.name,
                                            "type": "has_method",
                                        }
                                    )
                        elif isinstance(node, ast.FunctionDef):
                            graph["functions"].append(
                                {"name": node.name, "file": str(file_path)}
                            )
                            graph["edges"].append(
                                {
                                    "source": str(file_path),
                                    "target": node.name,
                                    "type": "contains",
                                }
                            )
                except Exception as e:  # noqa: BLE001
                    print(f"Failed to parse {file_path}: {e}")

    out_path = artifacts_dir / "knowledge_graph.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_graph()
