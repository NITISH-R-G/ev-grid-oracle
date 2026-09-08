import ast
import json
import os
import sys

def build_knowledge_graph(root_dir: str = ".") -> dict:
    graph: dict = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories robustly
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # Also ignore some common non-source directories
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'artifacts', 'docs', 'dashboard_output', 'web')]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Failed to read {filepath}: {e}", file=sys.stderr)
                continue

            try:
                tree = ast.parse(content, filename=filepath)
            except Exception as e:
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

            module_node_id = filepath
            graph["nodes"].append({
                "id": module_node_id,
                "type": "module",
                "name": file
            })

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_id = f"{module_node_id}::{node.name}"
                    graph["nodes"].append({
                        "id": class_id,
                        "type": "class",
                        "name": node.name
                    })
                    graph["edges"].append({
                        "source": module_node_id,
                        "target": class_id,
                        "type": "contains"
                    })
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_id = f"{module_node_id}::{node.name}"
                    graph["nodes"].append({
                        "id": func_id,
                        "type": "function",
                        "name": node.name
                    })
                    graph["edges"].append({
                        "source": module_node_id,
                        "target": func_id,
                        "type": "contains"
                    })

    return graph

if __name__ == "__main__":
    out_dir = "artifacts"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "knowledge_graph.json")

    graph = build_knowledge_graph(".")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Knowledge graph generated at {out_path}")
