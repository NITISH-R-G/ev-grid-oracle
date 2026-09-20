import ast
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_knowledge_graph() -> dict[str, Any]:
    graph: dict[str, Any] = {"nodes": [], "edges": []}

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in (
                "node_modules",
                "dist",
                "artifacts",
                "web",
                "assets",
                "dashboard_output",
                "docs",
                "ev_oracle_grpo_road",
                "ev_oracle_lora",
                "ev_oracle_merged_16bit",
                "ev_grid_oracle.egg-info",
                "build",
            )
        ]
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    module = ast.parse(source)

                    funcs: list[str] = []
                    classes: list[str] = []
                    for item in module.body:
                        if isinstance(item, ast.FunctionDef):
                            funcs.append(item.name)
                        elif isinstance(item, ast.ClassDef):
                            classes.append(item.name)

                    node = {
                        "id": file_path,
                        "type": "file",
                        "functions": funcs,
                        "classes": classes,
                    }

                    graph["nodes"].append(node)
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to parse {file_path}: {e}")

    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = generate_knowledge_graph()
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.info("Knowledge graph generated at artifacts/knowledge_graph.json")
