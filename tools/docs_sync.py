import ast
import os


def generate_api_docs(root_dir: str = ".") -> None:
    os.makedirs("docs/api", exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    # Create a path-safe filename to prevent collisions (e.g., server_app.md instead of just app.md)
                    rel_dir = os.path.relpath(dirpath, root_dir)
                    if rel_dir == ".":
                        safe_filename = file.replace(".py", ".md")
                    else:
                        safe_filename = f"{rel_dir.replace(os.sep, '_')}_{file.replace('.py', '.md')}"

                    doc_path = os.path.join("docs/api", safe_filename)

                    with open(doc_path, "w", encoding="utf-8") as doc_file:
                        doc_file.write(f"# API Documentation for `{file}`\n\n")

                        module_doc = ast.get_docstring(tree)
                        if module_doc:
                            doc_file.write(f"## Module Info\n\n{module_doc}\n\n")

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                doc_file.write(f"### Class: `{node.name}`\n\n")
                                class_doc = ast.get_docstring(node)
                                if class_doc:
                                    doc_file.write(f"{class_doc}\n\n")
                            elif isinstance(node, ast.FunctionDef):
                                doc_file.write(f"### Function: `{node.name}`\n\n")
                                func_doc = ast.get_docstring(node)
                                if func_doc:
                                    doc_file.write(f"{func_doc}\n\n")
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")


if __name__ == "__main__":
    generate_api_docs()
    print("API Documentation synced to docs/api/")
