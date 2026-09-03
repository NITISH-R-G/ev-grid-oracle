import os
import ast
import json


def generate_knowledge_graph() -> None:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    artifacts_dir = os.path.join(root_dir, "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    graph = {"files": [], "classes": [], "functions": [], "relationships": []}

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories
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

                graph["files"].append({"id": rel_path, "type": "file"})

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            class_id = f"{rel_path}:{node.name}"
                            graph["classes"].append(
                                {"id": class_id, "name": node.name, "file": rel_path}
                            )
                            graph["relationships"].append(
                                {
                                    "source": rel_path,
                                    "target": class_id,
                                    "type": "contains",
                                }
                            )

                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    func_id = f"{class_id}:{item.name}"
                                    graph["functions"].append(
                                        {
                                            "id": func_id,
                                            "name": item.name,
                                            "parent": class_id,
                                        }
                                    )
                                    graph["relationships"].append(
                                        {
                                            "source": class_id,
                                            "target": func_id,
                                            "type": "contains",
                                        }
                                    )

                        elif isinstance(node, ast.FunctionDef):
                            func_id = f"{rel_path}:{node.name}"
                            graph["functions"].append(
                                {"id": func_id, "name": node.name, "file": rel_path}
                            )
                            graph["relationships"].append(
                                {
                                    "source": rel_path,
                                    "target": func_id,
                                    "type": "contains",
                                }
                            )

                except Exception as e:
                    print(f"Failed to parse {rel_path}: {e}")

    out_path = os.path.join(artifacts_dir, "knowledge_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Knowledge graph generated in {out_path}")


if __name__ == "__main__":
    generate_knowledge_graph()
