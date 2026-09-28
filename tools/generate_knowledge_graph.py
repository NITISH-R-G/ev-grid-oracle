import ast
import json
import os


def generate_knowledge_graph(repo_path="."):
    graph = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk(repo_path):
        # Exclude hidden directories (like .git, .github, .venv, etc) and artifacts
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
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=filepath)

                module_id = filepath
                graph["nodes"].append({"id": module_id, "type": "module", "name": file})

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_id = f"{module_id}:{node.name}"
                        graph["nodes"].append(
                            {"id": class_id, "type": "class", "name": node.name}
                        )
                        graph["edges"].append(
                            {
                                "source": module_id,
                                "target": class_id,
                                "type": "contains",
                            }
                        )
                    elif isinstance(node, ast.FunctionDef):
                        func_id = f"{module_id}:{node.name}"
                        graph["nodes"].append(
                            {"id": func_id, "type": "function", "name": node.name}
                        )
                        graph["edges"].append(
                            {"source": module_id, "target": func_id, "type": "contains"}
                        )
            except Exception as e:
                print(f"Failed to parse {filepath}: {e}")

    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = generate_knowledge_graph()
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print("Knowledge graph generated at artifacts/knowledge_graph.json")
