import ast
import os


def generate_api_docs(root_dir="."):
    os.makedirs("docs/api", exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in ("node_modules", "venv", "dashboard_output", "artifacts", "docs")
        ]

        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    doc_content = f"# Documentation for {filepath}\n\n"
                    has_content = False

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            has_content = True
                            doc_content += f"## Function: `{node.name}`\n"
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += f"{docstring}\n\n"
                            else:
                                doc_content += "No description available.\n\n"
                        elif isinstance(node, ast.ClassDef):
                            has_content = True
                            doc_content += f"## Class: `{node.name}`\n"
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += f"{docstring}\n\n"
                            else:
                                doc_content += "No description available.\n\n"

                    if has_content:
                        safe_name = (
                            filepath.replace("/", "_")
                            .replace("\\", "_")
                            .replace(".py", ".md")
                        )
                        with open(
                            os.path.join("docs/api", safe_name), "w", encoding="utf-8"
                        ) as df:
                            df.write(doc_content)
                except Exception:  # nosec B110
                    pass


if __name__ == "__main__":
    generate_api_docs()
