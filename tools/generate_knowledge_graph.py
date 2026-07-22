import ast
import os
import json
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def generate_graph(repo_path: str = ".") -> None:
    info: Dict[str, List[Dict[str, Any]]] = {"modules": []}

    for root, _, files in os.walk(repo_path):
        if (
            "node_modules" in root
            or ".venv" in root
            or ".git" in root
            or "build" in root
            or "__pycache__" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path: str = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree: ast.Module = ast.parse(f.read(), filename=file_path)

                    classes: List[str] = []
                    functions: List[str] = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes.append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            functions.append(node.name)

                    if classes or functions:
                        info["modules"].append(
                            {
                                "path": file_path,
                                "classes": classes,
                                "functions": functions,
                            }
                        )
                except Exception as e:
                    logging.warning(f"Failed to parse {file_path}: {e}")

    os.makedirs("docs", exist_ok=True)
    try:
        with open("docs/knowledge_graph.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to write knowledge graph: {e}")


if __name__ == "__main__":
    generate_graph()
