#!/usr/bin/env python3
"""
Autonomous Architecture Diagram Generator
Builds a simple architectural dependency JSON object for the repository using AST parsing.
Outputs to artifacts/architecture_graph.json
"""

import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_architecture_graph(root_dir: str) -> dict[str, list[dict[str, Any]]]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".") and d not in ("venv", "node_modules", "artifacts")
        ]

        for file in filenames:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, file)
            rel_path = os.path.relpath(filepath, root_dir)
            nodes.append({"id": rel_path, "type": "file"})

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content)
            except Exception:
                continue  # nosec B112

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        edges.append(
                            {"source": rel_path, "target": alias.name, "type": "import"}
                        )
                elif isinstance(node, ast.ImportFrom) and node.module:
                    edges.append(
                        {
                            "source": rel_path,
                            "target": node.module,
                            "type": "import_from",
                        }
                    )

    return {"nodes": nodes, "edges": edges}


def main() -> None:
    root_dir = Path(__file__).parent.parent
    graph = generate_architecture_graph(str(root_dir))

    out_dir = root_dir / "artifacts"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "architecture_graph.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Architecture graph written to {out_file}")


if __name__ == "__main__":
    main()
