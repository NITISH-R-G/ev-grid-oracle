import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_architecture_graph(root_dir="."):
    graph = {"nodes": [], "edges": []}

    modules = set()
    dependencies = []

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                module_name = (
                    filepath.replace("/", ".").replace("\\", ".").replace(".py", "")
                )
                module_name = module_name.removeprefix(".")
                module_name = module_name.removeprefix(".")

                modules.add(module_name)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                dependencies.append((module_name, alias.name))
                        elif isinstance(node, ast.ImportFrom) and node.module:
                            dependencies.append((module_name, node.module))

                except Exception as e:  # noqa: BLE001 # noqa: BLE001
                    logger.warning(f"Failed to parse {filepath}: {e}")

    for module in modules:
        graph["nodes"].append({"id": module, "type": "module"})

    for src, dst in dependencies:
        graph["edges"].append({"source": src, "target": dst})

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.info("Architecture graph generated at artifacts/architecture_graph.json")


if __name__ == "__main__":
    generate_architecture_graph()
