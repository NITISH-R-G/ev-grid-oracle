import os
import ast
import json
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_python_file(filepath: str) -> dict[str, list[dict[str, str]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")  # noqa: BLE001
            return {"classes": [], "functions": []}

    info: dict[str, list[dict[str, str]]] = {"classes": [], "functions": []}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            info["classes"].append(
                {"name": node.name, "docstring": ast.get_docstring(node) or ""}
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            info["functions"].append(
                {"name": node.name, "docstring": ast.get_docstring(node) or ""}
            )
    return info


def generate_knowledge_graph():
    graph: dict[str, Any] = {"files": {}}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, ".")
                info = parse_python_file(filepath)

                if info["classes"] or info["functions"]:
                    graph["files"][rel_path] = info

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "knowledge_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    logger.info(
        f"Generated knowledge graph at {out_path} with {len(graph['files'])} indexed files."
    )


if __name__ == "__main__":
    generate_knowledge_graph()
