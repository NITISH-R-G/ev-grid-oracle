import ast
import os
import json
from typing import Any


def build_knowledge_graph(root_dir: str = ".") -> dict[str, list[dict[str, Any]]]:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories like .git, .github, .venv
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    graph["nodes"].append(
                        {"id": filepath, "type": "file", "label": file}
                    )

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
                                    "relation": "contains",
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
                                    "relation": "contains",
                                }
                            )
                except Exception as e:
                    print(f"Skipping {filepath} due to error: {e}")

    return graph


if __name__ == "__main__":
    kg = build_knowledge_graph()
    os.makedirs("docs", exist_ok=True)
    with open("docs/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(kg, f, indent=2)
    print("Knowledge graph generated at docs/knowledge_graph.json")
