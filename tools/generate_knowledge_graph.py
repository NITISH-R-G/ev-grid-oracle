#!/usr/bin/env python3
import os
import ast
import json
from pathlib import Path


def generate_graph():
    graph: dict[str, list[dict[str, str | int]]] = {"nodes": [], "edges": []}
    repo_root = Path(__file__).parent.parent

    # Simple AST-based knowledge graph for Python files
    for root, _, files in os.walk(repo_root):
        if (
            ".git" in root
            or "node_modules" in root
            or "venv" in root
            or ".venv" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_root)
                graph["nodes"].append({"id": rel_path, "group": 1})

                try:
                    with open(file_path, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_id = f"{rel_path}:{node.name}"
                            graph["nodes"].append(
                                {"id": class_id, "group": 2, "label": "Class"}
                            )
                            graph["edges"].append(
                                {
                                    "source": rel_path,
                                    "target": class_id,
                                    "type": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            func_id = f"{rel_path}:{node.name}"
                            graph["nodes"].append(
                                {"id": func_id, "group": 3, "label": "Function"}
                            )
                            graph["edges"].append(
                                {
                                    "source": rel_path,
                                    "target": func_id,
                                    "type": "contains",
                                }
                            )
                except Exception as e:
                    print(f"Failed to parse {file_path}: {e}")

    os.makedirs(repo_root / "artifacts", exist_ok=True)
    out_path = repo_root / "artifacts" / "knowledge_graph.json"
    with open(out_path, "w") as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph generated at {out_path}")


if __name__ == "__main__":
    generate_graph()
