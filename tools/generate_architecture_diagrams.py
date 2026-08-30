import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_architecture(root_dir="."):
    nodes = []
    links = []
    modules = set()

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        if 'node_modules' in dirnames:
            dirnames.remove('node_modules')

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)
            module_name = rel_path.replace(os.sep, '.').replace('.py', '')
            modules.add(module_name)
            nodes.append({"id": module_name, "group": 1})

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            links.append({"source": module_name, "target": alias.name, "value": 1})
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            links.append({"source": module_name, "target": node.module, "value": 1})
            except Exception as e:  # noqa: BLE001  # noqa: BLE001  # noqa: BLE001
                logger.warning(f"Error parsing {filepath}: {e}")

    # Filter external links for cleaner graph
    internal_links = [l for l in links if l["target"] in modules]

    graph = {
        "nodes": nodes,
        "links": internal_links
    }

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    logger.info("Architecture graph generated at artifacts/architecture_graph.json")

if __name__ == "__main__":
    generate_architecture()
