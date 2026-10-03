import ast
import os


def sync_docs():
    os.makedirs("docs/api", exist_ok=True)
    for root, _, files in os.walk("."):
        # Ignore hidden system directories
        if "/." in root or root.startswith("."):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r") as f:
                        tree = ast.parse(f.read())

                    doc_content = f"# API Reference for `{filepath}`\n\n"
                    has_docs = False

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += (
                                    f"## Class `{node.name}`\n{docstring}\n\n"
                                )
                                has_docs = True
                        elif isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += (
                                    f"## Function `{node.name}`\n{docstring}\n\n"
                                )
                                has_docs = True

                    if has_docs:
                        safe_name = filepath.replace("/", "_").replace(".py", ".md")
                        with open(f"docs/api/{safe_name}", "w") as out_f:
                            out_f.write(doc_content)
                except Exception:  # nosec B110
                    pass


if __name__ == "__main__":
    sync_docs()
