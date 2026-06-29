import os
import ast
import json

def generate_knowledge_graph(root_dir='.'):
    graph = {
        "nodes": [],
        "edges": []
    }

    file_id_counter = 1
    file_ids = {}

    for dirpath, _, filenames in os.walk(root_dir):
        if any(exclude in dirpath for exclude in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
            continue

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                file_id = f"file_{file_id_counter}"
                file_ids[filepath] = file_id
                file_id_counter += 1

                graph["nodes"].append({
                    "id": file_id,
                    "type": "file",
                    "path": filepath,
                    "label": filename
                })

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_id = f"class_{file_id}_{node.name}"
                        graph["nodes"].append({
                            "id": class_id,
                            "type": "class",
                            "label": node.name,
                            "file": filepath
                        })
                        graph["edges"].append({
                            "source": file_id,
                            "target": class_id,
                            "type": "contains"
                        })
                    elif isinstance(node, ast.FunctionDef):
                        func_id = f"func_{file_id}_{node.name}"
                        graph["nodes"].append({
                            "id": func_id,
                            "type": "function",
                            "label": node.name,
                            "file": filepath
                        })
                        graph["edges"].append({
                            "source": file_id,
                            "target": func_id,
                            "type": "contains"
                        })

            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

    os.makedirs('docs', exist_ok=True)
    with open('docs/knowledge_graph.json', 'w') as f:
        json.dump(graph, f, indent=2)

if __name__ == '__main__':
    generate_knowledge_graph()
