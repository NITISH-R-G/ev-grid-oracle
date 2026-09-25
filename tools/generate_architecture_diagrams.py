import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def generate_architecture_graph() -> None:
    graph: dict[str, list[dict[str, Any]]] = {"nodes": [], "edges": []}

    modules: dict[str, str] = {}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
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
            # Approximate module path e.g. ev_grid_oracle.env
            rel_path = os.path.relpath(filepath, ".")
            mod_path = rel_path.replace(".py", "").replace(os.sep, ".")
            mod_path = mod_path.removesuffix(".__init__")

            modules[filepath] = mod_path
            graph["nodes"].append(
                {"id": mod_path, "type": "module", "filepath": filepath}
            )

    for filepath, mod_name in modules.items():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            tree = ast.parse(source)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    # simplistic mapping
                    graph["edges"].append(
                        {"source": mod_name, "target": name.name, "type": "imports"}
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                graph["edges"].append(
                    {
                        "source": mod_name,
                        "target": node.module,
                        "type": "imports_from",
                    }
                )

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "architecture_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.info(f"Architecture graph written to {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_architecture_graph()
