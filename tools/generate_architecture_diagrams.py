import ast
import json
import os
from typing import Any


def extract_imports(filepath: str) -> list[str]:
    """Extract imported modules from a python file."""
    imports = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in tree.body:
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

    except Exception:
        pass

    return imports

def main() -> None:
    """Generate architecture graph."""
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    directories_to_scan = ["server", "ev_grid_oracle", "tools"]

    for dir_name in directories_to_scan:
        if not os.path.exists(dir_name):
            continue

        for root, dirs, files in os.walk(dir_name):
            if not root.startswith('.'):
                for file in files:
                    if file.endswith(".py"):
                        filepath = os.path.join(root, file)
                        nodes.append({"id": filepath, "type": "file"})

                        imports = extract_imports(filepath)
                        for imp in imports:
                            # Heuristic for internal vs external module
                            target_id = imp.replace('.', '/') + '.py'
                            edges.append({"source": filepath, "target": target_id, "type": "import"})

    graph = {"nodes": nodes, "edges": edges}

    output_dir = os.path.join(os.getcwd(), "artifacts")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "architecture_graph.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Architecture diagram generated at {out_path}")

if __name__ == "__main__":
    main()
