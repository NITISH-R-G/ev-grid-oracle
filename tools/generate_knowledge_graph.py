import ast
import json
import os


def build_graph(src_dir, dest_file):
    graph: dict[str, list[dict[str, str]]] = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk(src_dir):
        if not root.startswith("."):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, src_dir)
                    graph["nodes"].append({"id": rel_path, "type": "file"})
                    with open(path, "r", encoding="utf-8") as f:
                        try:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.ClassDef):
                                    graph["nodes"].append(
                                        {
                                            "id": f"{rel_path}:{node.name}",
                                            "type": "class",
                                        }
                                    )
                                    graph["edges"].append(
                                        {
                                            "source": rel_path,
                                            "target": f"{rel_path}:{node.name}",
                                        }
                                    )
                        except Exception:  # nosec B110  # noqa: BLE001
                            pass
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    build_graph(".", "artifacts/knowledge_graph.json")
