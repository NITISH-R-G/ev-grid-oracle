import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def generate_knowledge_graph() -> None:
    knowledge_graph: dict[str, Any] = {
        "modules": [],
        "classes": [],
        "functions": [],
        "files": [],
    }

    for root, dirs, files in os.walk("."):
        # Ignore hidden directories like .git, .venv, etc.
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Exclude common build directories
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if "build" in dirs:
            dirs.remove("build")
        if "dist" in dirs:
            dirs.remove("dist")

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()
            except Exception as e:
                logger.warning(f"Could not read {filepath}: {e}")
                continue

            knowledge_graph["files"].append(filepath)

            try:
                tree = ast.parse(source)
            except Exception as e:
                logger.warning(f"Could not parse {filepath}: {e}")
                continue

            module_info: dict[str, Any] = {
                "filepath": filepath,
                "name": file.replace(".py", ""),
                "docstring": ast.get_docstring(tree),
            }
            knowledge_graph["modules"].append(module_info)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info: dict[str, Any] = {
                        "name": node.name,
                        "filepath": filepath,
                        "docstring": ast.get_docstring(node),
                        "methods": [
                            n.name for n in node.body if isinstance(n, ast.FunctionDef)
                        ],
                    }
                    knowledge_graph["classes"].append(class_info)
                elif isinstance(node, ast.FunctionDef):
                    func_info: dict[str, Any] = {
                        "name": node.name,
                        "filepath": filepath,
                        "docstring": ast.get_docstring(node),
                    }
                    knowledge_graph["functions"].append(func_info)

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "knowledge_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=2)
    logger.info(f"Knowledge graph written to {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_knowledge_graph()
