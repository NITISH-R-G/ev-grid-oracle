import ast
import os


def update_docs():
    docs_path = "docs/api.md"
    os.makedirs("docs", exist_ok=True)

    with open(docs_path, "w") as f:
        f.write("# API Documentation\n\n")
        for root, _, files in os.walk("ev_grid_oracle"):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    with open(filepath, "r") as pyf:
                        try:
                            tree = ast.parse(pyf.read())
                            for node in ast.walk(tree):
                                if isinstance(node, ast.FunctionDef):
                                    doc = ast.get_docstring(node) or "No documentation."
                                    f.write(f"### `{node.name}`\n{doc}\n\n")
                        except Exception as e:
                            import logging

                            logging.warning(f"Failed to parse {filepath}: {e}")


if __name__ == "__main__":
    update_docs()
