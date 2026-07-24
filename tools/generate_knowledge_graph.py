import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def extract_info_from_ast(filepath: str) -> dict[str, list[dict[str, Any]]]:
    info: dict[str, list[dict[str, Any]]] = {"classes": [], "functions": []}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        logger.warning(f"Could not read file {filepath}: {e}")
        return info

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        logger.warning(f"Syntax error in {filepath}: {e}")
        return info

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info: dict[str, Any] = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "line_number": node.lineno,
            }
            info["classes"].append(class_info)
        elif isinstance(node, ast.FunctionDef):
            func_info: dict[str, Any] = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "line_number": node.lineno,
            }
            info["functions"].append(func_info)

    return info


def generate_knowledge_graph(root_dir: str = ".") -> dict[str, Any]:
    graph: dict[str, Any] = {}

    skip_dirs = {
        ".git",
        ".github",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
        "artifacts",
        ".cursor",
        ".mypy_cache",
        ".pytest_cache",
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                info = extract_info_from_ast(filepath)
                if info["classes"] or info["functions"]:
                    graph[filepath] = info

    return graph


def main() -> None:
    logger.info("Generating knowledge graph...")
    graph = generate_knowledge_graph()

    output_dir = "artifacts"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "knowledge_graph.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    logger.info(f"Knowledge graph written to {output_file}")


if __name__ == "__main__":
    main()
