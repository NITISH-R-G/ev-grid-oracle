import ast
import os


def sync_docs():
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "venv" in dirs:
            dirs.remove("venv")
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, ".")
                safe_name = (
                    rel_path.replace("/", "_").replace("\\", "_").replace(".py", ".md")
                )
                doc_path = os.path.join("docs/api", safe_name)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=rel_path)

                    doc_content = f"# API Documentation for `{rel_path}`\n\n"

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        doc_content += (
                            f"## Module Documentation\n\n```text\n{module_doc}\n```\n\n"
                        )

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc_content += f"## Class `{node.name}`\n\n"
                            class_doc = ast.get_docstring(node)
                            if class_doc:
                                doc_content += f"```text\n{class_doc}\n```\n\n"
                        elif isinstance(node, ast.FunctionDef):
                            doc_content += f"## Function `{node.name}`\n\n"
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                doc_content += f"```text\n{func_doc}\n```\n\n"

                    with open(doc_path, "w", encoding="utf-8") as df:
                        df.write(doc_content)
                except Exception:
                    pass  # nosec B110


if __name__ == "__main__":
    sync_docs()
