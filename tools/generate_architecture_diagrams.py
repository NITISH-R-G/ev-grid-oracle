import os
import ast
import json


def generate_architecture_diagrams() -> None:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    artifacts_dir = os.path.join(root_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    graph = {"nodes": [], "edges": []}

    # First pass: collect all modules (files)
    modules = set()
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                "docs",
                "artifacts",
                "dashboard_output",
                "node_modules",
                "dist",
                "build",
                "__pycache__",
            )
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                module_name = rel_path.replace(os.sep, ".")[:-3]  # remove .py
                if module_name.endswith(".__init__"):
                    module_name = module_name[:-9]
                modules.add(module_name)
                graph["nodes"].append({"id": module_name, "type": "module"})

    # Second pass: detect imports to create edges
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                "docs",
                "artifacts",
                "dashboard_output",
                "node_modules",
                "dist",
                "build",
                "__pycache__",
            )
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                source_module = rel_path.replace(os.sep, ".")[:-3]
                if source_module.endswith(".__init__"):
                    source_module = source_module[:-9]

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)

                    for node in tree.body:
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                # if alias.name in modules:
                                graph["edges"].append(
                                    {"source": source_module, "target": alias.name}
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                # if node.module in modules:
                                graph["edges"].append(
                                    {"source": source_module, "target": node.module}
                                )

                except Exception as e:
                    print(f"Failed to parse {rel_path}: {e}")

    # Remove duplicates from edges
    unique_edges = []
    seen = set()
    for edge in graph["edges"]:
        key = (edge["source"], edge["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)
    graph["edges"] = unique_edges

    out_path = os.path.join(artifacts_dir, "architecture_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Architecture graph generated in {out_path}")


if __name__ == "__main__":
    generate_architecture_diagrams()
