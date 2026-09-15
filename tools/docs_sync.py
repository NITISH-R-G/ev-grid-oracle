import ast
import os


def sync_docs(root_dir: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories like .git and .venv
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, root_dir)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                docstring = ast.get_docstring(tree)

                doc_content = f"# API Documentation for `{rel_path}`\n\n"
                if docstring:
                    doc_content += f"{docstring}\n\n"

                has_items = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        has_items = True
                        doc_content += f"## Class `{node.name}`\n"
                        class_doc = ast.get_docstring(node)
                        if class_doc:
                            doc_content += f"{class_doc}\n"
                        doc_content += "\n"
                    elif isinstance(node, ast.FunctionDef):
                        has_items = True
                        doc_content += f"## Function `{node.name}`\n"
                        func_doc = ast.get_docstring(node)
                        if func_doc:
                            doc_content += f"{func_doc}\n"
                        doc_content += "\n"

                if has_items or docstring:
                    safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                    out_path = os.path.join(output_dir, safe_name)
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write(doc_content)

            except Exception:  # nosec B110  # noqa: BLE001
                pass


if __name__ == "__main__":
    sync_docs(".", "docs/api/")
