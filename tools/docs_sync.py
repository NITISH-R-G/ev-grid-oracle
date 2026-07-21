import ast
import os
import logging


def generate_api_docs() -> None:
    doc_content = "# API Documentation\n\n"

    for root, _, files in os.walk("."):
        if any(
            ignored in root
            for ignored in [".venv", "node_modules", ".git", "build", ".cursor"]
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read())

                    module_doc = ast.get_docstring(tree)
                    has_content = False
                    file_content = f"## `{filepath}`\n\n"
                    if module_doc:
                        file_content += f"{module_doc}\n\n"
                        has_content = True

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc = ast.get_docstring(node)
                            if doc:
                                file_content += f"### Class: `{node.name}`\n{doc}\n\n"
                                has_content = True
                        elif isinstance(node, ast.FunctionDef):
                            doc = ast.get_docstring(node)
                            if doc:
                                file_content += (
                                    f"### Function: `{node.name}`\n{doc}\n\n"
                                )
                                has_content = True

                    if has_content:
                        doc_content += file_content
                except Exception as e:
                    logging.warning(f"Failed to process {filepath}: {e}")

    os.makedirs("docs", exist_ok=True)
    with open("docs/api_reference.md", "w", encoding="utf-8") as f:
        f.write(doc_content)

    print("Documentation synced to docs/api_reference.md")


if __name__ == "__main__":
    generate_api_docs()
