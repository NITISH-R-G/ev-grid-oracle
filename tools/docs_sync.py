import os
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_docs(repo_root: str):
    docs_dir = os.path.join(repo_root, "docs", "api")
    os.makedirs(docs_dir, exist_ok=True)

    for root, dirs, files in os.walk(repo_root):
        if any(d.startswith(".") for d in root.split(os.sep)):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, repo_root)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                doc_content = f"# {rel_path}\n\n"

                module_doc = ast.get_docstring(tree)
                if module_doc:
                    doc_content += f"{module_doc}\n\n"

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        doc_content += f"## Class: {node.name}\n\n"
                        class_doc = ast.get_docstring(node)
                        if class_doc:
                            doc_content += f"{class_doc}\n\n"

                    elif isinstance(node, ast.FunctionDef):
                        doc_content += f"## Function: {node.name}\n\n"
                        func_doc = ast.get_docstring(node)
                        if func_doc:
                            doc_content += f"{func_doc}\n\n"

                # Save doc
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                out_path = os.path.join(docs_dir, safe_name)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(doc_content)

            except Exception as e:
                logger.warning(f"Failed to process docs for {rel_path}: {e}")  # noqa: BLE001


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    generate_docs(repo_root)
    logger.info("Docs synchronized successfully.")
