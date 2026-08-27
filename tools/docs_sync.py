import ast
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_docs():
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    doc_content = f"# Documentation for `{filepath}`\n\n"

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            doc_content += f"## Class: `{node.name}`\n"
                            if docstring:
                                doc_content += f"{docstring}\n\n"
                            else:
                                doc_content += "*No documentation available.*\n\n"
                        elif isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            doc_content += f"### Function: `{node.name}`\n"
                            if docstring:
                                doc_content += f"{docstring}\n\n"
                            else:
                                doc_content += "*No documentation available.*\n\n"

                    safe_filename = filepath.replace("/", "_").replace("\\", "_")
                    doc_filepath = os.path.join("docs", "api", f"{safe_filename}.md")

                    with open(doc_filepath, "w", encoding="utf-8") as out:
                        out.write(doc_content)
                except Exception as e:
                    logger.warning(f"Failed to generate docs for {filepath}: {e}")


if __name__ == "__main__":
    sync_docs()
