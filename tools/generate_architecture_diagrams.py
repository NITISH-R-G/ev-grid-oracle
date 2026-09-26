#!/usr/bin/env python3
"""Autonomous Architecture Diagram generator."""

import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_architecture_diagrams(repo_root: Path, output_file: Path):
    output_file.parent.mkdir(parents=True, exist_ok=True)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    # Simple registry to keep track of added nodes
    added_nodes = set()

    def add_node(node_id: str, node_type: str):
        if node_id not in added_nodes:
            nodes.append({"id": node_id, "type": node_type})
            added_nodes.add(node_id)

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = Path(root) / file
            rel_path = str(filepath.relative_to(repo_root))

            # Use module path as node ID (e.g., server/app.py -> server.app)
            module_id = rel_path.replace(".py", "").replace("/", ".")
            module_id = module_id.removesuffix(".__init__")

            add_node(module_id, "module")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                module_ast = ast.parse(content)

                for node in ast.walk(module_ast):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            target = alias.name
                            add_node(target, "external_module")
                            edges.append(
                                {
                                    "source": module_id,
                                    "target": target,
                                    "type": "imports",
                                }
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            target = node.module
                            add_node(
                                target,
                                "module"
                                if target.startswith(("server", "ev_grid_oracle"))
                                else "external_module",
                            )
                            edges.append(
                                {
                                    "source": module_id,
                                    "target": target,
                                    "type": "imports_from",
                                }
                            )

            except Exception as e:
                print(f"Error parsing {filepath}: {e}")

    graph = {"nodes": nodes, "edges": edges}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    root = Path.cwd()
    out_file = root / "artifacts" / "architecture_graph.json"
    generate_architecture_diagrams(root, out_file)
    print(f"Successfully generated architecture graph to {out_file}")
