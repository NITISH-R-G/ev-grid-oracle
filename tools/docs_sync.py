import ast
import os
from pathlib import Path


def sync_docs() -> None:
    output_dir = Path("docs/api")
    output_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                        tree = ast.parse(source, filename=filepath)

                    doc_content = f"# Documentation for `{filepath}`\n\n"

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        doc_content += f"## Module Documentation\n\n{module_doc}\n\n"

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc_content += f"## Class: `{node.name}`\n"
                            class_doc = ast.get_docstring(node)
                            if class_doc:
                                doc_content += f"\n{class_doc}\n"
                            doc_content += "\n"
                        elif isinstance(node, ast.FunctionDef):
                            doc_content += f"### Function: `{node.name}`\n"
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                doc_content += f"\n{func_doc}\n"
                            doc_content += "\n"

                    # Create safe filename to prevent collisions
                    safe_filename = filepath.replace(os.sep, "_").replace(".py", ".md")
                    safe_filename = safe_filename.removeprefix("_")

                    output_file = output_dir / safe_filename
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(doc_content)
                except Exception:  # noqa: BLE001, S110
                    pass


if __name__ == "__main__":
    import logging

    logger = logging.getLogger(__name__)
    sync_docs()
    logger.warning("Generated documentation.")
