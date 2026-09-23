import ast
import json
import os


def extract_imports(filepath: str) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return imports


def main():
    nodes = []
    edges = []

    for root, dirs, files in os.walk("."):
        if ".git" in root or ".venv" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.normpath(os.path.join(root, file))
                module_name = filepath.replace(os.sep, ".").replace(".py", "")
                module_name = module_name.removeprefix(".")

                nodes.append({"id": module_name, "type": "python_module"})

                imports = extract_imports(filepath)
                for imp in imports:
                    edges.append({"source": module_name, "target": imp})

    graph = {"nodes": nodes, "edges": edges}

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    main()
