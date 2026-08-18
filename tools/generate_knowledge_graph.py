import ast
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def extract_entities(filepath: Path) -> list[dict[str, Any]]:
    """Extract entities (classes, functions, etc.) from a Python file to form a knowledge graph."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError as e:
            logger.warning(f"SyntaxError parsing {filepath}: {e}")
            return []

    entities: list[dict[str, Any]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            entities.append({"type": "Class", "name": node.name, "file": str(filepath)})
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    entities.append(
                        {
                            "type": "Method",
                            "name": sub_node.name,
                            "parent": node.name,
                            "file": str(filepath),
                        }
                    )
        elif isinstance(node, ast.FunctionDef):
            entities.append(
                {"type": "Function", "name": node.name, "file": str(filepath)}
            )

    return entities


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting knowledge graph generation...")

    root_dir = Path(".")
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_path = artifacts_dir / "knowledge_graph.json"

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

                # Add file as a node
                graph["nodes"].append(
                    {"id": str(filepath), "type": "File", "name": filename}
                )

                entities = extract_entities(filepath)
                for entity in entities:
                    node_id = f"{entity['file']}::{entity['name']}"
                    if entity["type"] == "Method":
                        node_id = (
                            f"{entity['file']}::{entity['parent']}::{entity['name']}"
                        )

                    graph["nodes"].append(
                        {"id": node_id, "type": entity["type"], "name": entity["name"]}
                    )
                    graph["edges"].append(
                        {"source": str(filepath), "target": node_id, "type": "CONTAINS"}
                    )

                    if entity["type"] == "Method":
                        parent_id = f"{entity['file']}::{entity['parent']}"
                        graph["edges"].append(
                            {
                                "source": parent_id,
                                "target": node_id,
                                "type": "HAS_METHOD",
                            }
                        )

    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump(graph, out_f, indent=2)

    logger.info(f"Knowledge graph generation complete. Output saved to {out_path}")


if __name__ == "__main__":
    main()
