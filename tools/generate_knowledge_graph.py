import ast
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_knowledge_graph(root_dir="."):
    graph = {"files": {}, "classes": {}, "functions": {}}

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories (e.g. .git, .github)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    graph["files"][filepath] = {
                        "imports": [],
                        "classes": [],
                        "functions": [],
                    }

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                graph["files"][filepath]["imports"].append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                graph["files"][filepath]["imports"].append(node.module)
                        elif isinstance(node, ast.ClassDef):
                            class_info: dict[str, str | list[str]] = {
                                "file": filepath,
                                "methods": [],
                            }
                            if ast.get_docstring(node):
                                class_info["docstring"] = ast.get_docstring(node)

                            methods = []
                            for n in node.body:
                                if isinstance(n, ast.FunctionDef):
                                    methods.append(n.name)
                            class_info["methods"] = methods
                            graph["classes"][node.name] = class_info
                            graph["files"][filepath]["classes"].append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            func_info: dict[str, str] = {"file": filepath}
                            if ast.get_docstring(node):
                                func_info["docstring"] = ast.get_docstring(node)
                            graph["functions"][node.name] = func_info
                            graph["files"][filepath]["functions"].append(node.name)

                except Exception as e:  # noqa: BLE001 # noqa: BLE001
                    logger.warning(f"Failed to parse {filepath}: {e}")

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.info("Knowledge graph generated at artifacts/knowledge_graph.json")


if __name__ == "__main__":
    generate_knowledge_graph()
