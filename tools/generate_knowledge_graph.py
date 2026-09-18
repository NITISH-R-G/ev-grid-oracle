import ast
import json
import os
from typing import Any


def main() -> None:
    print("Starting generate_knowledge_graph.py...")
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    root_dir = "."
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories like .git
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        # Also ignore node_modules, venv, etc
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

                node: dict[str, Any] = {
                    "id": filepath,
                    "type": "file",
                    "classes": [],
                    "functions": [],
                }

                try:
                    tree = ast.parse(content, filename=filepath)
                    for item in ast.walk(tree):
                        if isinstance(item, ast.ClassDef):
                            node["classes"].append(item.name)
                        elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            node["functions"].append(item.name)
                except SyntaxError:
                    pass
                except Exception:  # nosec B110 # noqa: BLE001
                    pass

                graph["nodes"].append(node)

            except Exception:  # nosec B110 # noqa: BLE001
                pass

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "knowledge_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Knowledge graph generated at {out_path}")


if __name__ == "__main__":
    main()
