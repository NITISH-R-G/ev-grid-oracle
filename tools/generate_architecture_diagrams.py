import ast
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_architecture_graph() -> dict[str, Any]:
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

                node = {"id": file_path, "type": "file"}
                graph["nodes"].append(node)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    module = ast.parse(source)
                    for item in module.body:
                        if isinstance(item, ast.Import):
                            for name in item.names:
                                graph["edges"].append(
                                    {
                                        "source": file_path,
                                        "target": name.name,
                                        "type": "import",
                                    }
                                )
                        elif isinstance(item, ast.ImportFrom) and item.module:
                            graph["edges"].append(
                                {
                                    "source": file_path,
                                    "target": item.module,
                                    "type": "import_from",
                                }
                            )
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to process {file_path}: {e}")

    return graph


if __name__ == "__main__":
    os.makedirs("artifacts", exist_ok=True)
    graph = generate_architecture_graph()
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.info("Architecture graph generated at artifacts/architecture_graph.json")
