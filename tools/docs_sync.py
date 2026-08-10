import ast
import os
from pathlib import Path


def generate_docs() -> None:
    """Generates markdown API documentation for Python files."""
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in [
                "venv",
                "env",
                "__pycache__",
                "node_modules",
                "dashboard_output",
                "build",
                "dist",
                "docs",
            ]
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    has_content = False

                    # Create a path-safe markdown filename
                    rel_path = os.path.relpath(file_path, ".")
                    safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                    doc_path = docs_dir / safe_name

                    doc_content = f"# API Reference: `{rel_path}`\n\n"

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        doc_content += f"{module_doc}\n\n"

                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            has_content = True
                            doc_content += f"## Class `{node.name}`\n\n"
                            class_doc = ast.get_docstring(node)
                            if class_doc:
                                doc_content += f"{class_doc}\n\n"

                            for item in node.body:
                                if isinstance(
                                    item, (ast.FunctionDef, ast.AsyncFunctionDef)
                                ):
                                    doc_content += f"### Method `{item.name}`\n\n"
                                    method_doc = ast.get_docstring(item)
                                    if method_doc:
                                        doc_content += f"{method_doc}\n\n"

                        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            has_content = True
                            doc_content += f"## Function `{node.name}`\n\n"
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                doc_content += f"{func_doc}\n\n"

                    if has_content:
                        with open(doc_path, "w", encoding="utf-8") as out_f:
                            out_f.write(doc_content)

                except Exception as e:
                    print(f"Error documenting {file_path}: {e}")

    print("Generated API documentation successfully.")


if __name__ == "__main__":
    generate_docs()
