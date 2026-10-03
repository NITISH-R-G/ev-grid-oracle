import ast
import json
import os


def generate_architecture():
    nodes = []
    edges = []

    for root, _, files in os.walk("."):
        # Ignore hidden directories
        if "/." in root or root.startswith("."):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                nodes.append({"id": filepath, "type": "module"})

                try:
                    with open(filepath, "r") as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                edges.append(
                                    {
                                        "source": filepath,
                                        "target": alias.name,
                                        "type": "imports",
                                    }
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                edges.append(
                                    {
                                        "source": filepath,
                                        "target": node.module,
                                        "type": "imports",
                                    }
                                )
                except Exception:  # nosec B110
                    pass

    graph = {"nodes": nodes, "edges": edges}
    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture()
