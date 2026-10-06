import os
import ast
import json
from typing import Any

def generate_architecture_graph(root_dir: str, output_file: str) -> None:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)

                module_name = rel_path.replace(os.sep, '.')[:-3]
                nodes.append({"id": module_name, "type": "module"})

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        source = f.read()

                    tree = ast.parse(source)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                edges.append({
                                    "source": module_name,
                                    "target": alias.name
                                })
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                edges.append({
                                    "source": module_name,
                                    "target": node.module
                                })
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    generate_architecture_graph(".", "artifacts/architecture_graph.json")
