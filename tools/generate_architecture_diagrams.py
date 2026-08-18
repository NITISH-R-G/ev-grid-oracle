import ast
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def extract_dependencies(filepath: Path) -> list[str]:
    """Extract module dependencies from a Python file to form an architecture graph."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError as e:
            logger.warning(f"SyntaxError parsing {filepath}: {e}")
            return []

    dependencies: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            dependencies.append(node.module)

    return dependencies


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting architecture diagram generation...")

    root_dir = Path(".")
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "architecture_graph.json"

    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        # Also ignore some common build/virtualenv dirs if they are not hidden
        dirnames[:] = [
            d
            for d in dirnames
            if d not in ("venv", "build", "dist", "node_modules", "dashboard_output")
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = Path(dirpath) / filename

                # Create a simple module name from path
                rel_path = filepath.relative_to(root_dir)
                module_name = str(rel_path).replace(os.sep, ".").replace(".py", "")

                graph["nodes"].append(
                    {"id": module_name, "type": "Module", "file": str(filepath)}
                )

                dependencies = extract_dependencies(filepath)
                for dep in dependencies:
                    # We add target nodes lazily, or rely on visualization tools to handle missing targets
                    graph["edges"].append(
                        {"source": module_name, "target": dep, "type": "IMPORTS"}
                    )

    # Add unique target nodes that might be external dependencies
    existing_nodes = {node["id"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        if edge["target"] not in existing_nodes:
            graph["nodes"].append(
                {"id": edge["target"], "type": "ExternalModule", "file": None}
            )
            existing_nodes.add(edge["target"])

    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump(graph, out_f, indent=2)

    logger.info(f"Architecture graph generation complete. Output saved to {out_path}")


if __name__ == "__main__":
    main()
