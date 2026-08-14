import ast
import json
import os


def generate_knowledge_graph():
    graph = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        # Explicitly exclude hidden directories like .git or .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # also ignore root directories that start with .
        if root == "." or not any(part.startswith('.') for part in root.split(os.sep)[1:]):

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    graph["nodes"].append({"id": filepath, "type": "file", "label": file})

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                class_id = f"{filepath}::{node.name}"
                                graph["nodes"].append({"id": class_id, "type": "class", "label": node.name})
                                graph["edges"].append({"source": filepath, "target": class_id, "type": "contains"})
                            elif isinstance(node, ast.FunctionDef):
                                func_id = f"{filepath}::{node.name}"
                                graph["nodes"].append({"id": func_id, "type": "function", "label": node.name})
                                graph["edges"].append({"source": filepath, "target": func_id, "type": "contains"})
                    except Exception as e:
                        print(f"Failed to parse {filepath}: {e}")

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", 'w') as f:
        json.dump(graph, f, indent=2)
    print("Knowledge graph generated at artifacts/knowledge_graph.json")

if __name__ == "__main__":
    generate_knowledge_graph()