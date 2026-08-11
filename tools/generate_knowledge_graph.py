import os
import ast
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GRAPH_OUTPUT = "knowledge_graph.json"


def extract_dependencies(filepath: str) -> list[str]:
    """Extracts imported modules from a Python file."""
    dependencies = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)

        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                dependencies.append(node.module)
    except SyntaxError as e:
        logger.warning(f"Failed to parse imports in {filepath}: {e}")
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")

    return list(set(dependencies))


def generate_knowledge_graph():
    """Generates a graph connecting files to their dependencies and structural components."""
    graph: dict[str, dict[str, list[str]]] = {}

    for root, _, files in os.walk("."):
        # Ignore hidden system directories
        if os.path.basename(root).startswith(".") or any(
            part.startswith(".") and part != "." for part in root.split(os.sep)
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                dependencies = extract_dependencies(filepath)

                # Further graph logic could include classes and functions similar to docs_sync.py

                graph[filepath] = {
                    "dependencies": dependencies,
                    "classes": [],  # Can be populated using ast similar to docs_sync
                    "functions": [],  # Can be populated using ast similar to docs_sync
                }

                # Quick parse for classes and functions
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            graph[filepath]["classes"].append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            graph[filepath]["functions"].append(node.name)
                except Exception:
                    pass

    with open(GRAPH_OUTPUT, "w", encoding="utf-8") as out_f:
        json.dump(graph, out_f, indent=2)
    logger.info(f"Knowledge graph generated and saved to {GRAPH_OUTPUT}")


if __name__ == "__main__":
    generate_knowledge_graph()
