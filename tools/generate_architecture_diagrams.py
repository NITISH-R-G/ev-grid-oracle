import ast
import logging
import os
import re

logger = logging.getLogger(__name__)


def generate_architecture() -> None:
    """Generates an interactive Mermaid.js diagram from Python AST parsing."""
    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", "architecture_graph.md")

    nodes = []
    edges = []

    for root, dnames, fnames in os.walk("."):
        dnames[:] = [d for d in dnames if not d.startswith(".")]
        if "node_modules" in root or "dist" in root:
            continue

        for fname in fnames:
            if fname.endswith(".py"):
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source, filename=filepath)
                    safe_file_id = re.sub(r"[^a-zA-Z0-9]", "_", filepath)
                    nodes.append(f'  {safe_file_id}["{filepath}"]')

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                safe_target = re.sub(r"[^a-zA-Z0-9]", "_", alias.name)
                                nodes.append(f'  {safe_target}["{alias.name}"]')
                                edges.append(f"  {safe_file_id} --> {safe_target}")
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                safe_target = re.sub(r"[^a-zA-Z0-9]", "_", node.module)
                                nodes.append(f'  {safe_target}["{node.module}"]')
                                edges.append(f"  {safe_file_id} --> {safe_target}")

                except Exception:  # noqa: BLE001
                    logger.warning(f"Failed to parse {filepath}")
                    continue

    # Deduplicate
    nodes = list(set(nodes))
    edges = list(set(edges))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Graph\n\n```mermaid\ngraph TD\n")
        f.write("\n".join(nodes))
        f.write("\n")
        f.write("\n".join(edges))
        f.write("\n```\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Generating architecture graph...")
    generate_architecture()
    logger.info("Architecture graph complete.")
