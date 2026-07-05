import os
import ast


def sync_docs():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(repo_root, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    api_doc_path = os.path.join(docs_dir, "api.md")

    with open(api_doc_path, "w", encoding="utf-8") as f:
        f.write("# API Documentation\n\n")

        for root, _, files in os.walk(repo_root):
            if (
                "venv" in root
                or ".venv" in root
                or ".git" in root
                or "node_modules" in root
            ):
                continue

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, repo_root)

                    try:
                        with open(filepath, "r", encoding="utf-8") as code_file:
                            tree = ast.parse(code_file.read())

                        has_docs = False
                        doc_content = f"## `{rel_path}`\n\n"

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                docstring = ast.get_docstring(node)
                                if docstring:
                                    has_docs = True
                                    doc_content += (
                                        f"### Class: `{node.name}`\n\n{docstring}\n\n"
                                    )

                            elif isinstance(node, ast.FunctionDef):
                                docstring = ast.get_docstring(node)
                                if docstring:
                                    has_docs = True
                                    doc_content += f"### Function: `{node.name}`\n\n{docstring}\n\n"

                        if has_docs:
                            f.write(doc_content)

                    except Exception as e:
                        print(f"Failed to parse {rel_path}: {e}")


if __name__ == "__main__":
    sync_docs()
