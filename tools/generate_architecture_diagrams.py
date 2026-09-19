import ast
import json
import os
from typing import Any


def generate_architecture_diagrams() -> None:
    architecture_graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    modules = set()

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        # ignore some other obvious non-source directories
        dirs[:] = [
            d for d in dirs if d not in ("node_modules", "artifacts", "web", "docs")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            # Make module name out of filepath
            module_name = (
                filepath.replace("./", "").replace("/", ".").replace(".py", "")
            )
            if module_name.endswith(".__init__"):
                module_name = module_name[:-9]

            modules.add(module_name)

            node = {"id": module_name, "type": "module", "filepath": filepath}
            architecture_graph["nodes"].append(node)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue  # nosec B112

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            for walk_node in ast.walk(tree):
                if isinstance(walk_node, ast.Import):
                    for alias in walk_node.names:
                        architecture_graph["edges"].append(
                            {
                                "source": module_name,
                                "target": alias.name,
                                "type": "import",
                            }
                        )
                elif isinstance(walk_node, ast.ImportFrom):
                    if walk_node.module:
                        # Handle relative imports naively
                        target = walk_node.module
                        if walk_node.level > 0:
                            parts = module_name.split(".")
                            base = ".".join(parts[: -walk_node.level])
                            target = f"{base}.{target}" if base else target

                        architecture_graph["edges"].append(
                            {"source": module_name, "target": target, "type": "import"}
                        )

    # deduplicate nodes and edges based on sets
    unique_nodes = {node["id"]: node for node in architecture_graph["nodes"]}
    architecture_graph["nodes"] = list(unique_nodes.values())

    unique_edges = set()
    filtered_edges = []
    for edge in architecture_graph["edges"]:
        # only keep internal imports if possible or at least deduplicate
        tup = (edge["source"], edge["target"])
        if tup not in unique_edges:
            unique_edges.add(tup)
            filtered_edges.append(edge)

    architecture_graph["edges"] = filtered_edges

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(architecture_graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams()
