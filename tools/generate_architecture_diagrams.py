import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_architecture(repo_root: str) -> dict:
    graph: dict[str, list[dict[str, str]]] = {"nodes": [], "edges": []}

    modules = set()

    for root, dirs, files in os.walk(repo_root):
        if any(d.startswith(".") for d in root.split(os.sep)):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, repo_root)
            module_name = rel_path.replace(os.sep, ".").replace(".py", "")

            modules.add(module_name)
            graph["nodes"].append({"id": module_name, "label": module_name})

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            graph["edges"].append(
                                {"source": module_name, "target": alias.name}
                            )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            graph["edges"].append(
                                {"source": module_name, "target": node.module}
                            )

            except Exception as e:
                logger.warning(f"Failed to parse {rel_path}: {e}")

    return graph


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    graph = generate_architecture(repo_root)

    os.makedirs(os.path.join(repo_root, "artifacts"), exist_ok=True)
    out_path = os.path.join(repo_root, "artifacts", "architecture_graph.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    logger.info(f"Architecture diagram written to {out_path}")
