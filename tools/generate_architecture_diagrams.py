import ast
import json
import os
from pathlib import Path
from typing import Any


def main():
    root_dir = Path(".")
    artifacts_dir = root_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Explicitly ignore standard virtual env or build folders
        ignore_dirs = ["venv", "build", "dist", "node_modules"]
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(root_dir))

                graph["nodes"].append({"id": rel_path, "type": "file"})

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                except Exception:
                    continue  # nosec B112

                for node in tree.body:
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            graph["edges"].append(
                                {
                                    "source": rel_path,
                                    "target": name.name,
                                    "type": "imports",
                                }
                            )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        graph["edges"].append(
                            {
                                "source": rel_path,
                                "target": node.module,
                                "type": "imports_from",
                            }
                        )

    out_path = artifacts_dir / "architecture_graph.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Generated Architecture Diagram graph to {out_path}")


if __name__ == "__main__":
    main()
