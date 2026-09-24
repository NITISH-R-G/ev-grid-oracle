import ast
import json
import os
from pathlib import Path
from typing import Any


def generate_architecture_diagrams(root_dir: str = "."):
    graph: dict[str, Any] = {"nodes": [], "edges": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories (e.g., .git, .venv, .github)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    module = ast.parse(content)

                    # Add file node
                    graph["nodes"].append({"id": filepath, "type": "file"})

                    for node in ast.walk(module):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["edges"].append(
                                    {
                                        "source": filepath,
                                        "target": alias.name,
                                        "type": "imports",
                                    }
                                )
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                graph["edges"].append(
                                    {
                                        "source": filepath,
                                        "target": node.module,
                                        "type": "imports_from",
                                    }
                                )
                except Exception:  # nosec B110
                    pass

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams()
