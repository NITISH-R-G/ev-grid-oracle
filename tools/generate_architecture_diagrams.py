import os
import ast
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_imports(filepath: str) -> list[str]:
    imports: list[str] = []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")  # noqa: BLE001
            return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return list(set(imports))


def generate_architecture_diagrams():
    graph: dict[str, list[str]] = {}

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, ".")
                imports = parse_imports(filepath)
                graph[rel_path] = imports

    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "architecture_graph.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    logger.info(
        f"Generated architecture graph at {out_path} representing {len(graph)} files."
    )


if __name__ == "__main__":
    generate_architecture_diagrams()
