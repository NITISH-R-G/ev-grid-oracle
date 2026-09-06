import os
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_docs(root_dir="."):
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    doc_content = f"# Documentation for `{filepath}`\n\n"
                    has_content = False

                    if ast.get_docstring(tree):
                        doc_content += f"## Module Docstring\n\n```text\n{ast.get_docstring(tree)}\n```\n\n"
                        has_content = True

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc_content += f"## Class `{node.name}`\n\n"
                            if ast.get_docstring(node):
                                doc_content += f"```text\n{ast.get_docstring(node)}\n```\n\n"
                            has_content = True
                        elif isinstance(node, ast.FunctionDef):
                            # Skip if part of a class (handled recursively if needed, but keeping it simple)
                            doc_content += f"### Function `{node.name}`\n\n"
                            if ast.get_docstring(node):
                                doc_content += f"```text\n{ast.get_docstring(node)}\n```\n\n"
                            has_content = True

                    if has_content:
                        # Construct path-safe filename
                        safe_name = filepath.replace("/", "_").replace("\\", "_").replace(".py", ".md")
                        out_path = os.path.join("docs/api", safe_name)
                        with open(out_path, "w", encoding="utf-8") as out_f:
                            out_f.write(doc_content)
                        logger.info(f"Generated docs for {filepath}")

                except Exception as e: # noqa: BLE001
                    logger.warning(f"Failed to generate docs for {filepath}: {e}")

if __name__ == "__main__":
    sync_docs()
