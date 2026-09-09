import ast
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_docs():
    """Generates markdown documentation for Python files using the ast module."""
    for root, dirs, files in os.walk("."):
        # Ignore hidden directories like .git, .github, .venv, etc.
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        file_content = f.read()

                    tree = ast.parse(file_content)

                    doc_content = f"# Documentation for {filepath}\n\n"

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        doc_content += f"## Module Documentation\n\n{module_doc}\n\n"

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc_content += f"## Class: {node.name}\n\n"
                            class_doc = ast.get_docstring(node)
                            if class_doc:
                                doc_content += f"{class_doc}\n\n"

                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    doc_content += f"### Method: {item.name}\n\n"
                                    method_doc = ast.get_docstring(item)
                                    if method_doc:
                                        doc_content += f"{method_doc}\n\n"
                        elif isinstance(node, ast.FunctionDef) and getattr(node, 'col_offset', 0) == 0:
                            doc_content += f"## Function: {node.name}\n\n"
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                doc_content += f"{func_doc}\n\n"

                    os.makedirs("docs/api", exist_ok=True)
                    # Construct path-safe filenames by incorporating the relative directory path
                    safe_name = filepath.replace("/", "_").replace("\\", "_").replace(".py", ".md")
                    output_path = os.path.join("docs/api", safe_name)

                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(doc_content)

                except Exception as e:
                    logger.warning(f"Error parsing file {filepath}: {e}") # noqa: BLE001

    logger.info("Documentation generated in docs/api/")

if __name__ == "__main__":
    generate_docs()
