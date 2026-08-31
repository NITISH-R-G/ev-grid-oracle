import ast
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def generate_knowledge_graph() -> None:
    knowledge_graph: dict[str, dict[str, Any]] = {}

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Also ignore some standard build/artifact directories
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                "node_modules",
                "artifacts",
                "build",
                "dist",
                "dashboard_output",
                "docs",
                "web",
            )
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                file_info: dict[str, list[dict[str, Any]]] = {
                    "classes": [],
                    "functions": [],
                }

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        file_info["classes"].append(
                            {"name": node.name, "docstring": ast.get_docstring(node)}
                        )
                    elif isinstance(node, ast.FunctionDef) or isinstance(
                        node, ast.AsyncFunctionDef
                    ):
                        file_info["functions"].append(
                            {"name": node.name, "docstring": ast.get_docstring(node)}
                        )

                knowledge_graph[filepath] = file_info

            except SyntaxError as e:
                logger.warning("SyntaxError parsing %s: %s", filepath, e)
            except OSError as e:
                logger.warning("OSError reading %s: %s", filepath, e)

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
