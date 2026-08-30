import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_knowledge_graph(root_dir="."):
    graph = {
        "files": [],
        "classes": [],
        "functions": [],
        "imports": []
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories like .git, .github, .venv
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        if 'node_modules' in dirnames:
            dirnames.remove('node_modules')

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                rel_path = os.path.relpath(filepath, root_dir)
                graph["files"].append(rel_path)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        graph["classes"].append({
                            "name": node.name,
                            "file": rel_path,
                            "docstring": ast.get_docstring(node)
                        })
                    elif isinstance(node, ast.FunctionDef):
                        graph["functions"].append({
                            "name": node.name,
                            "file": rel_path,
                            "docstring": ast.get_docstring(node)
                        })
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            graph["imports"].append({
                                "module": alias.name,
                                "file": rel_path
                            })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            graph["imports"].append({
                                "module": node.module,
                                "file": rel_path
                            })
            except Exception as e:  # noqa: BLE001  # noqa: BLE001
                logger.warning(f"Failed to parse {filepath}: {e}")

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)
    logger.info("Knowledge graph generated at artifacts/knowledge_graph.json")

if __name__ == "__main__":
    generate_knowledge_graph()
