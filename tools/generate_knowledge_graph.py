import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_metadata(filepath: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"classes": [], "functions": [], "docstring": None}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        metadata["docstring"] = ast.get_docstring(tree)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                metadata["classes"].append(
                    {"name": node.name, "docstring": ast.get_docstring(node)}
                )
            elif isinstance(node, ast.FunctionDef):
                metadata["functions"].append(
                    {"name": node.name, "docstring": ast.get_docstring(node)}
                )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to parse {filepath}: {e}")
    return metadata


def generate_knowledge_graph(root_dir: str) -> dict[str, dict[str, Any]]:
    graph: dict[str, dict[str, Any]] = {}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                graph[filepath] = extract_metadata(filepath)
    return graph


def main() -> None:
    graph = generate_knowledge_graph(".")
    out_file = "knowledge_graph.json"
    try:
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2)
        logger.info(f"Knowledge graph successfully written to {out_file}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to write knowledge graph: {e}")


if __name__ == "__main__":
    main()
