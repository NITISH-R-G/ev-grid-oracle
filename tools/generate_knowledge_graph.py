import ast  # noqa: EXE002
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_knowledge_graph(repo_root: str) -> dict:
    graph: dict[str, list[dict[str, str]]] = {
        "files": [],
        "classes": [],
        "functions": [],
        "dependencies": [],
    }

    for root, dirs, files in os.walk(repo_root):
        if any(d.startswith(".") for d in root.split(os.sep)):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, repo_root)

            file_node = {"id": rel_path, "type": "file", "path": rel_path}
            graph["files"].append(file_node)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_node = {
                            "id": f"{rel_path}:{node.name}",
                            "type": "class",
                            "name": node.name,
                            "file": rel_path,
                        }
                        graph["classes"].append(class_node)
                        graph["dependencies"].append(
                            {
                                "source": rel_path,
                                "target": f"{rel_path}:{node.name}",
                                "type": "contains",
                            }
                        )

                    elif isinstance(node, ast.FunctionDef):
                        func_node = {
                            "id": f"{rel_path}:{node.name}",
                            "type": "function",
                            "name": node.name,
                            "file": rel_path,
                        }
                        graph["functions"].append(func_node)
                        graph["dependencies"].append(
                            {
                                "source": rel_path,
                                "target": f"{rel_path}:{node.name}",
                                "type": "contains",
                            }
                        )

            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to parse {rel_path}: {e}")

    return graph


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    graph = generate_knowledge_graph(repo_root)

    os.makedirs(os.path.join(repo_root, "artifacts"), exist_ok=True)
    out_path = os.path.join(repo_root, "artifacts", "knowledge_graph.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    logger.info(f"Knowledge graph written to {out_path}")
