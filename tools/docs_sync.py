import ast
import logging
import os
import re

logger = logging.getLogger(__name__)


def generate_docs() -> None:
    """Generates markdown documentation from Python docstrings."""
    os.makedirs(os.path.join("docs", "api"), exist_ok=True)

    for root, dnames, fnames in os.walk("."):
        # Explicitly bypass hidden directories
        dnames[:] = [d for d in dnames if not d.startswith(".")]

        # Avoid traversing node_modules or large build dirs
        if "node_modules" in root or "dist" in root:
            continue

        for fname in fnames:
            if fname.endswith(".py"):
                filepath = os.path.join(root, fname)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source, filename=filepath)

                    doc_content = []
                    module_docstring = ast.get_docstring(tree)

                    if module_docstring:
                        doc_content.append(f"# `{filepath}`\n\n{module_docstring}\n")
                    else:
                        doc_content.append(f"# `{filepath}`\n")

                    has_content = False
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                            doc = ast.get_docstring(node)
                            if doc:
                                has_content = True
                                header_prefix = (
                                    "## " if isinstance(node, ast.ClassDef) else "### "
                                )
                                doc_content.append(
                                    f"{header_prefix} `{node.name}`\n\n{doc}\n"
                                )

                    if has_content or module_docstring:
                        # Construct path-safe filename
                        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", filepath) + ".md"
                        out_path = os.path.join("docs", "api", safe_name)
                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write("\n".join(doc_content))

                except Exception:  # noqa: BLE001
                    logger.warning(f"Failed to parse {filepath}")
                    continue


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Syncing docs...")
    generate_docs()
    logger.info("Docs sync complete.")
