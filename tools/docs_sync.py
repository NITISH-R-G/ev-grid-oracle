import ast
import os


def sync_docs(repo_path: str) -> None:
    docs_dir = os.path.join(repo_path, "docs", "api")
    os.makedirs(docs_dir, exist_ok=True)

    for root, _, files in os.walk(repo_path):
        if (
            "venv" in root
            or ".venv" in root
            or "node_modules" in root
            or ".git" in root
            or "__pycache__" in root
        ):
            continue

        for file in files:
            if file.endswith(".py") and not file.startswith("test_"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    doc_content = f"# API Reference for `{filepath}`\n\n"
                    has_content = False

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += (
                                    f"## Class `{node.name}`\n\n{docstring}\n\n"
                                )
                                has_content = True
                        elif isinstance(node, ast.FunctionDef) or isinstance(
                            node, ast.AsyncFunctionDef
                        ):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += (
                                    f"### Function `{node.name}`\n\n{docstring}\n\n"
                                )
                                has_content = True

                    if has_content:
                        rel_path = os.path.relpath(filepath, repo_path).replace(
                            os.sep, "_"
                        )
                        doc_filename = os.path.join(docs_dir, f"{rel_path}.md")
                        with open(doc_filename, "w", encoding="utf-8") as out_f:
                            out_f.write(doc_content)
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")


if __name__ == "__main__":
    sync_docs(".")
    print("Documentation synced successfully.")
