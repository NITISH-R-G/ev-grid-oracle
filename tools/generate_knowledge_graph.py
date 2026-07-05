import os
import ast
import json
import networkx as nx


def generate_knowledge_graph():
    graph = nx.DiGraph()
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    for root, _, files in os.walk(repo_root):
        if (
            "venv" in root
            or ".venv" in root
            or ".git" in root
            or "node_modules" in root
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, repo_root)
                graph.add_node(rel_path, type="file")

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_name = f"{rel_path}:{node.name}"
                            graph.add_node(class_name, type="class")
                            graph.add_edge(rel_path, class_name, relation="contains")

                        elif isinstance(node, ast.FunctionDef):
                            func_name = f"{rel_path}:{node.name}"
                            graph.add_node(func_name, type="function")
                            graph.add_edge(rel_path, func_name, relation="contains")
                except Exception as e:
                    print(f"Failed to parse {rel_path}: {e}")

    # Export to JSON
    data = nx.node_link_data(graph)
    os.makedirs(os.path.join(repo_root, "artifacts"), exist_ok=True)
    with open(os.path.join(repo_root, "artifacts", "knowledge_graph.json"), "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
