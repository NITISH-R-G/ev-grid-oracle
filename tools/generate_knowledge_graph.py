import ast
import json
import os
import networkx as nx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_knowledge_graph():
    """Generates a knowledge graph of files, classes, and functions using the ast module."""
    knowledge_graph = []

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

                    file_info = {
                        "type": "file",
                        "path": filepath,
                        "classes": [],
                        "functions": []
                    }

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            class_info = {
                                "name": node.name,
                                "methods": []
                            }
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    class_info["methods"].append(item.name)
                            file_info["classes"].append(class_info)
                        elif isinstance(node, ast.FunctionDef) and getattr(node, 'col_offset', 0) == 0:
                            # Only top-level functions
                            file_info["functions"].append(node.name)

                    knowledge_graph.append(file_info)

                except Exception as e:
                    logger.warning(f"Error parsing file {filepath}: {e}") # noqa: BLE001

    os.makedirs("artifacts", exist_ok=True)
    output_path = "artifacts/knowledge_graph.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_graph, f, indent=4)
    logger.info(f"Knowledge graph generated at {output_path}")

if __name__ == "__main__":
    generate_knowledge_graph()
