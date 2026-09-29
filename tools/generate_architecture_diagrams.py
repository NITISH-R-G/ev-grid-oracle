import ast
import json
import os


def generate_graph(root_dir="."):
    nodes = []
    edges = []

    for root, dnames, files in os.walk(root_dir):
        dnames[:] = [d for d in dnames if not d.startswith(".") and d != "node_modules"]
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
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                edges.append(
                                    {"source": module_name, "target": alias.name}
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                edges.append(
                                    {"source": module_name, "target": node.module}
                                )
                except Exception:  # nosec B110
                    pass

    return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = generate_graph()
    with open("artifacts/architecture_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
