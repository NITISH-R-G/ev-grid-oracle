import os
import ast
import json
def generate_architecture(src_dir, dest_file):
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    arch: dict[str, list[dict[str, str]]] = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, src_dir)
                arch["nodes"].append({"id": rel_path, "type": "module"})
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                arch["edges"].append({"source": rel_path, "target": alias.name, "relation": "imports"})
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            arch["edges"].append({"source": rel_path, "target": node.module, "relation": "imports_from"})
                except Exception as e:  # noqa: BLE001
                    pass
    with open(dest_file, 'w', encoding='utf-8') as f:
        json.dump(arch, f, indent=2)
if __name__ == '__main__':
    generate_architecture('.', 'artifacts/architecture_graph.json')
