import ast
import json
import os
from typing import Any


def get_imports(filepath: str) -> list[str]:
    imports: list[str] = []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception: # noqa: BLE001
            return []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)

    return imports

def main() -> None:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_set: set[str] = set()

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if "node_modules" in root or "artifacts" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                # Use module-like path representation for id
                rel_path = os.path.relpath(filepath, ".")
                mod_name = rel_path.replace(os.path.sep, ".").replace(".py", "")

                if mod_name not in node_set:
                    nodes.append({"id": mod_name, "type": "module"})
                    node_set.add(mod_name)

                imports = get_imports(filepath)
                for imp in imports:
                    if imp not in node_set:
                        nodes.append({"id": imp, "type": "dependency"})
                        node_set.add(imp)
                    edges.append({"source": mod_name, "target": imp, "type": "imports"})

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

if __name__ == "__main__":
    main()
