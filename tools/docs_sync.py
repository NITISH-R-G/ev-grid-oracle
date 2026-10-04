import ast
import os


def generate_docs():
    docs_dir = "docs/api"
    os.makedirs(docs_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py") and file != "docs_sync.py":
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    doc_content = f"# Documentation for `{filepath}`\n\n"

                    if ast.get_docstring(tree):
                        doc_content += (
                            f"## Module Docstring\n\n{ast.get_docstring(tree)}\n\n"
                        )

                    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
                    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]

                    if classes:
                        doc_content += "## Classes\n\n"
                        for cls in classes:
                            doc_content += f"### `{cls.name}`\n"
                            if ast.get_docstring(cls):
                                doc_content += f"{ast.get_docstring(cls)}\n\n"
                            else:
                                doc_content += "No docstring provided.\n\n"

                    if functions:
                        doc_content += "## Functions\n\n"
                        for func in functions:
                            doc_content += f"### `{func.name}`\n"
                            if ast.get_docstring(func):
                                doc_content += f"{ast.get_docstring(func)}\n\n"
                            else:
                                doc_content += "No docstring provided.\n\n"

                    # create path-safe filename
                    safe_name = (
                        filepath.replace("/", "_").replace("\\", "_").replace(".", "_")
                        + ".md"
                    )
                    out_path = os.path.join(docs_dir, safe_name)

                    with open(out_path, "w", encoding="utf-8") as out:
                        out.write(doc_content)
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")


if __name__ == "__main__":
    generate_docs()
