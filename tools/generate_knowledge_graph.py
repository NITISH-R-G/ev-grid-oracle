import ast
import json
import os


def generate_graph():
    nodes = []
    edges = []
    for root, _, files in os.walk("."):
        # Ignore hidden system directories to ensure robustness
        if "/." in root or root.startswith("."):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                nodes.append({"id": filepath, "type": "file"})
                try:
                    with open(filepath, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            nodes.append(
                                {"id": f"{filepath}:{node.name}", "type": "class"}
                            )
                            edges.append(
                                {
                                    "source": filepath,
                                    "target": f"{filepath}:{node.name}",
                                }
                            )
                        elif isinstance(node, ast.FunctionDef):
                            nodes.append(
                                {"id": f"{filepath}:{node.name}", "type": "function"}
                            )
                            edges.append(
                                {
                                    "source": filepath,
                                    "target": f"{filepath}:{node.name}",
                                }
                            )
                except Exception:  # nosec B110
                    pass

    graph = {"nodes": nodes, "edges": edges}
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_graph()
