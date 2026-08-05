#!/usr/bin/env python3
import ast
import json
import os
from typing import Any


def generate_knowledge_graph() -> None:
    graph: dict[str, Any] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".github" in dirs:
            dirs.remove(".github")
        if "venv" in dirs:
            dirs.remove("venv")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    file_node = {"id": filepath, "type": "file", "label": file}
                    graph["nodes"].append(file_node)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_id = f"{filepath}::{node.name}"
                            graph["nodes"].append(
                                {"id": class_id, "type": "class", "label": node.name}
                            )
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": class_id,
                                    "type": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            func_id = f"{filepath}::{node.name}"
                            graph["nodes"].append(
                                {"id": func_id, "type": "function", "label": node.name}
                            )
                            graph["edges"].append(
                                {
                                    "source": filepath,
                                    "target": func_id,
                                    "type": "contains",
                                }
                            )

                except Exception as e:  # noqa: BLE001
                    print(f"Failed to parse {filepath}: {e}")

    with open("knowledge_graph.json", "w", encoding="utf-8") as out:
        json.dump(graph, out, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
