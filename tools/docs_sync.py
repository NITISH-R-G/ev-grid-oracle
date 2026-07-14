import ast
import os
import logging


def sync_docs() -> None:
    docs = "# API Documentation\n\n"
    for root, _, files in os.walk("."):
        if "venv" in root or ".git" in root or ".venv" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r") as f:
                        tree = ast.parse(f.read())
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc = ast.get_docstring(node)
                            if doc:
                                docs += f"## Class {node.name}\n{doc}\n\n"
                        elif isinstance(node, ast.FunctionDef):
                            doc = ast.get_docstring(node)
                            if doc:
                                docs += f"## Function {node.name}\n{doc}\n\n"
                except Exception as e:
                    logging.warning(f"Error parsing {path}: {e}")
    with open("docs/api.md", "w") as f:
        f.write(docs)


if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    sync_docs()
