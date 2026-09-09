import ast
import json
import os
import networkx as nx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_architecture_diagrams():
    """Generates an architecture dependency graph using the ast module."""
    nodes = []
    edges = []

    for root, dirs, files in os.walk("."):
        # Ignore hidden directories like .git, .github, .venv, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_content = f.read()

                    tree = ast.parse(file_content)

                    nodes.append({
                        "id": filepath,
                        "type": "file"
                    })

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                edges.append({
                                    "source": filepath,
                                    "target": alias.name
                                })
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                edges.append({
                                    "source": filepath,
                                    "target": node.module
                                })

                except Exception as e:
                    logger.warning(f"Error parsing file {filepath}: {e}") # noqa: BLE001

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    os.makedirs("artifacts", exist_ok=True)
    output_path = "artifacts/architecture_graph.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4)
    logger.info(f"Architecture diagram generated at {output_path}")

if __name__ == "__main__":
    generate_architecture_diagrams()
