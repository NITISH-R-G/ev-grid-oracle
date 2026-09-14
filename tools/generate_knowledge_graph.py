import os
import ast
import json

def generate_graph(src_dir, dest_file):
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    graph = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk(src_dir):
        # Exclude hidden directories explicitly
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, src_dir)
                graph["nodes"].append({"id": rel_path, "type": "file"})

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            cls_id = f"{rel_path}:{node.name}"
                            graph["nodes"].append({"id": cls_id, "type": "class"})
                            graph["edges"].append({"source": rel_path, "target": cls_id, "relation": "contains"})
                        elif isinstance(node, ast.FunctionDef):
                            func_id = f"{rel_path}:{node.name}"
                            graph["nodes"].append({"id": func_id, "type": "function"})
                            graph["edges"].append({"source": rel_path, "target": func_id, "relation": "contains"})
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")

    with open(dest_file, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2)

if __name__ == '__main__':
    generate_graph('.', 'artifacts/knowledge_graph.json')
