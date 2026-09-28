import ast
import json
import os


def generate_architecture_diagrams(repo_path="."):
    graph = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ("artifacts", "node_modules", "dist", "build", "__pycache__")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            module_name = (
                os.path.relpath(filepath, repo_path)
                .replace(".py", "")
                .replace(os.sep, ".")
            )

            graph["nodes"].append({"id": module_name, "type": "module"})

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=filepath)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            graph["edges"].append(
                                {
                                    "source": module_name,
                                    "target": alias.name,
                                    "type": "imports",
                                }
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            graph["edges"].append(
                                {
                                    "source": module_name,
                                    "target": node.module,
                                    "type": "imports_from",
                                }
                            )
            except Exception as e:
                print(f"Failed to parse {filepath}: {e}")

    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = generate_architecture_diagrams()
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print("Architecture graph generated at artifacts/architecture_graph.json")
