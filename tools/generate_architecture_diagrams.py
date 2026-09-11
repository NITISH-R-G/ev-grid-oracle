import ast
import json
import os


def build_arch_graph(src_dir, dest_file):
    graph: dict[str, list[dict[str, str]]] = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk(src_dir):
        if not root.startswith("."):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, src_dir)
                    graph["nodes"].append({"id": rel_path, "type": "module"})
                    with open(path, "r", encoding="utf-8") as f:
                        try:
                            tree = ast.parse(f.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.Import):
                                    for alias in node.names:
                                        graph["edges"].append(
                                            {"source": rel_path, "target": alias.name}
                                        )
                                elif isinstance(node, ast.ImportFrom):
                                    if node.module:
                                        graph["edges"].append(
                                            {"source": rel_path, "target": node.module}
                                        )
                        except Exception:  # nosec B110  # noqa: BLE001
                            pass
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    with open(dest_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    build_arch_graph(".", "artifacts/architecture_graph.json")
