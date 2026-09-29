import ast
import os


def generate_docs(root_dir=".", output_dir="docs/api"):
    os.makedirs(output_dir, exist_ok=True)

    for root, dnames, files in os.walk(root_dir):
        dnames[:] = [d for d in dnames if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, root_dir)
                doc_filename = rel_path.replace("/", "_").replace(".py", ".md")
                doc_filepath = os.path.join(output_dir, doc_filename)

                try:
                    with open(filepath, "r") as f:
                        tree = ast.parse(f.read())

                    content = f"# Documentation for `{rel_path}`\n\n"

                    docstring = ast.get_docstring(tree)
                    if docstring:
                        content += f"{docstring}\n\n"

                    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
                    if classes:
                        content += "## Classes\n\n"
                        for c in classes:
                            content += f"### {c.name}\n"
                            c_doc = ast.get_docstring(c)
                            if c_doc:
                                content += f"{c_doc}\n"
                            content += "\n"

                    funcs = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
                    if funcs:
                        content += "## Functions\n\n"
                        for f_node in funcs:
                            content += f"### {f_node.name}\n"
                            f_doc = ast.get_docstring(f_node)
                            if f_doc:
                                content += f"{f_doc}\n"
                            content += "\n"

                    with open(doc_filepath, "w") as f_out:
                        f_out.write(content)
                except Exception:  # nosec B110
                    pass


if __name__ == "__main__":
    generate_docs()
