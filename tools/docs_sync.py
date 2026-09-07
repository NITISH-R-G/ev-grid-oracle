import ast
import os


def parse_file(filepath: str) -> str:
    """Parse a python file and generate markdown documentation."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"Error reading {filepath}: {e}"

    try:
        tree = ast.parse(content)
    except Exception as e:
        return f"Error parsing {filepath}: {e}"

    doc = f"# API Documentation: `{filepath}`\n\n"

    module_doc = ast.get_docstring(tree)
    if module_doc:
        doc += f"{module_doc}\n\n"

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            doc += f"## Class: `{node.name}`\n\n"
            class_doc = ast.get_docstring(node)
            if class_doc:
                doc += f"{class_doc}\n\n"

            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    doc += f"### Method: `{child.name}`\n\n"
                    method_doc = ast.get_docstring(child)
                    if method_doc:
                        doc += f"{method_doc}\n\n"

        elif isinstance(node, ast.FunctionDef):
            doc += f"## Function: `{node.name}`\n\n"
            func_doc = ast.get_docstring(node)
            if func_doc:
                doc += f"{func_doc}\n\n"

    return doc

def main() -> None:
    """Generate docs for all python files in specific directories."""
    output_dir = os.path.join(os.getcwd(), "docs", "api")
    os.makedirs(output_dir, exist_ok=True)

    directories_to_scan = ["server", "ev_grid_oracle", "tools"]

    for dir_name in directories_to_scan:
        if not os.path.exists(dir_name):
            continue

        for root, dirs, files in os.walk(dir_name):
            if not root.startswith('.'):
                for file in files:
                    if file.endswith(".py") and file != "__init__.py":
                        filepath = os.path.join(root, file)
                        doc_content = parse_file(filepath)

                        # Create path-safe filename
                        safe_name = filepath.replace(os.path.sep, "_").replace(".py", ".md")
                        out_path = os.path.join(output_dir, safe_name)

                        with open(out_path, "w", encoding="utf-8") as f:
                            f.write(doc_content)

    print(f"Documentation generated in {output_dir}")

if __name__ == "__main__":
    main()
