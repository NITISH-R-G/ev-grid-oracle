import ast
import json
import os
import sys

def build_architecture_graph(root_dir: str = ".") -> dict:
    graph: dict = {"nodes": [], "edges": []}
    modules_found = set()
    imports = []

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories robustly
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # Also ignore some common non-source directories
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'artifacts', 'docs', 'dashboard_output', 'web')]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            # Make the module name look somewhat like Python import paths
            module_name = os.path.splitext(os.path.relpath(filepath, root_dir))[0].replace(os.sep, ".")
            modules_found.add(module_name)

            graph["nodes"].append({
                "id": module_name,
                "type": "module"
            })

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Failed to read {filepath}: {e}", file=sys.stderr)
                continue

            try:
                tree = ast.parse(content, filename=filepath)
            except Exception as e:
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({"source": module_name, "target": alias.name})
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Handle relative imports naively
                        if node.level > 0:
                            parts = module_name.split(".")
                            base = ".".join(parts[:-node.level]) if len(parts) > node.level else ""
                            target = f"{base}.{node.module}" if base else node.module
                        else:
                            target = node.module
                        imports.append({"source": module_name, "target": target})

    for imp in imports:
        # Only include edges if the target looks like an internal module (optional heuristic)
        # But we will include them all to show external dependencies too.
        graph["edges"].append({
            "source": imp["source"],
            "target": imp["target"],
            "type": "imports"
        })

        # Add external module as a node if it wasn't found in our walk
        if imp["target"] not in modules_found:
            graph["nodes"].append({
                "id": imp["target"],
                "type": "external_module"
            })
            modules_found.add(imp["target"])

    return graph

if __name__ == "__main__":
    out_dir = "artifacts"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "architecture_graph.json")

    graph = build_architecture_graph(".")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Architecture graph generated at {out_path}")
