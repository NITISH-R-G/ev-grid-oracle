import ast
import os

def generate_docs() -> None:
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    classes = []
                    functions = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            classes.append(node)
                        elif isinstance(node, ast.FunctionDef) and not getattr(node, 'is_method', False):
                            functions.append(node)

                    if classes or functions:
                        # Construct path-safe filename
                        rel_path = os.path.relpath(filepath, ".")
                        safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                        out_path = os.path.join("docs", "api", safe_name)

                        with open(out_path, "w", encoding="utf-8") as out:
                            out.write(f"# API Reference: `{rel_path}`\n\n")

                            if classes:
                                out.write("## Classes\n\n")
                                for c in classes:
                                    out.write(f"### `{c.name}`\n")
                                    doc = ast.get_docstring(c) or "No documentation available."
                                    out.write(f"{doc}\n\n")

                            if functions:
                                out.write("## Functions\n\n")
                                for f_node in functions:
                                    out.write(f"### `{f_node.name}`\n")
                                    doc = ast.get_docstring(f_node) or "No documentation available."
                                    out.write(f"{doc}\n\n")
                except Exception as e:
                    pass # noqa: BLE001

if __name__ == "__main__":
    generate_docs()
    print("Documentation synced to docs/api/")
