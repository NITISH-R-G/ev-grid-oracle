import ast
import json
import os
from typing import Any


def main() -> None:
    print("Starting generate_architecture_diagrams.py...")
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    root_dir = "."
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames[:] = [
            d for d in dirnames if d not in ("node_modules", "venv", "__pycache__")
        ]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                graph["nodes"].append({"id": filepath, "type": "module"})

                try:
                    tree = ast.parse(content, filename=filepath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["edges"].append(
                                    {"source": filepath, "target": alias.name}
                                )
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            graph["edges"].append(
                                {"source": filepath, "target": node.module}
                            )
                except SyntaxError:
                    pass
                except Exception:  # nosec B110 # noqa: BLE001
                    pass
            except Exception:  # nosec B110 # noqa: BLE001
                pass

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "architecture_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Architecture graph generated at {out_path}")


if __name__ == "__main__":
    main()
