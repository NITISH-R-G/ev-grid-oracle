import ast
import json
import os
from typing import Any


def build_knowledge_graph(root_dir: str = ".") -> dict[str, list[dict[str, Any]]]:
    nodes = []
    edges = []

    for root, dnames, files in os.walk(root_dir):
        dnames[:] = [d for d in dnames if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                module_name = (
                    filepath.replace("./", "").replace("/", ".").replace(".py", "")
                )
                nodes.append({"id": module_name, "type": "module"})

                try:
                    with open(filepath, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = f"{module_name}.{node.name}"
                            nodes.append({"id": class_name, "type": "class"})
                            edges.append(
                                {
                                    "source": module_name,
                                    "target": class_name,
                                    "relation": "contains",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            func_name = f"{module_name}.{node.name}"
                            nodes.append({"id": func_name, "type": "function"})
                            edges.append(
                                {
                                    "source": module_name,
                                    "target": func_name,
                                    "relation": "contains",
                                }
                            )
                except Exception:  # nosec B110
                    pass

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = build_knowledge_graph()
    with open("artifacts/knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
