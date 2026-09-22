import ast
import json
import os
from pathlib import Path
from typing import Any


def main():
    root_dir = Path(".")
    artifacts_dir = root_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    knowledge: dict[str, list[dict[str, Any]]] = {"entities": [], "relationships": []}

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

                knowledge["entities"].append(
                    {"id": rel_path, "type": "file", "name": file}
                )

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                except Exception:
                    continue  # nosec B112

                for node in tree.body:
                    if isinstance(node, ast.ClassDef):
                        class_id = f"{rel_path}:{node.name}"
                        knowledge["entities"].append(
                            {"id": class_id, "type": "class", "name": node.name}
                        )
                        knowledge["relationships"].append(
                            {"source": rel_path, "target": class_id, "type": "contains"}
                        )

                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                func_id = f"{class_id}:{item.name}"
                                knowledge["entities"].append(
                                    {"id": func_id, "type": "method", "name": item.name}
                                )
                                knowledge["relationships"].append(
                                    {
                                        "source": class_id,
                                        "target": func_id,
                                        "type": "has_method",
                                    }
                                )

                    elif isinstance(node, ast.FunctionDef):
                        func_id = f"{rel_path}:{node.name}"
                        knowledge["entities"].append(
                            {"id": func_id, "type": "function", "name": node.name}
                        )
                        knowledge["relationships"].append(
                            {"source": rel_path, "target": func_id, "type": "contains"}
                        )

    out_path = artifacts_dir / "knowledge_graph.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, indent=2)

    print(f"Generated Knowledge Graph to {out_path}")


if __name__ == "__main__":
    main()
