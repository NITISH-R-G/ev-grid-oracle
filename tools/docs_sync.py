import ast
import os


def sync_docs():
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        # Explicitly exclude hidden directories like .git or .github
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # also ignore root directories that start with .
        if root == "." or not any(part.startswith('.') for part in root.split(os.sep)[1:]):

            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    rel_path = os.path.relpath(filepath, ".")
                    safe_name = rel_path.replace(os.path.sep, "_").replace(".py", ".md")
                    doc_filepath = os.path.join(docs_dir, safe_name)

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()

                        tree = ast.parse(content)

                        doc_content = f"# Documentation for {rel_path}\n\n"

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                doc_content += f"## Class: {node.name}\n\n"
                                if ast.get_docstring(node):
                                    doc_content += f"{ast.get_docstring(node)}\n\n"
                            elif isinstance(node, ast.FunctionDef):
                                doc_content += f"### Function: {node.name}\n\n"
                                if ast.get_docstring(node):
                                    doc_content += f"{ast.get_docstring(node)}\n\n"

                        with open(doc_filepath, 'w') as f:
                            f.write(doc_content)
                    except Exception as e:
                        print(f"Failed to sync docs for {filepath}: {e}")

if __name__ == "__main__":
    sync_docs()