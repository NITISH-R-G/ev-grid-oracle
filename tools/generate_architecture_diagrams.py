import os
import ast
import json
from typing import Any

def generate_architecture_graph(root_dir: str) -> dict[str, list[dict[str, str]]]:
    nodes: list[dict[str, str]] = []
    edges: list[dict[str, str]] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)
            module_name = rel_path.replace(os.sep, '.')[:-3]

            nodes.append({"id": module_name, "type": "module"})

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                module = ast.parse(content)
                for node in module.body:
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            edges.append({"source": module_name, "target": alias.name})
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        edges.append({"source": module_name, "target": node.module})
            except Exception as e: # noqa: BLE001
                pass

    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    graph = generate_architecture_graph(root)

    out_dir = os.path.join(root, 'artifacts')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'architecture_graph.json')

    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)
    print(f"Generated architecture graph at {out_path}")
