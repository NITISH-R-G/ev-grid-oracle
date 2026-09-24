import ast
import os
from pathlib import Path


def generate_docs(root_dir: str = "."):
    output_dir = Path("docs/api")
    output_dir.mkdir(parents=True, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories (e.g., .git, .venv, .github)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    module = ast.parse(content)

                    doc_content = f"# Documentation for `{filepath}`\n\n"

                    for node in module.body:
                        if isinstance(node, ast.ClassDef):
                            doc_content += f"## Class `{node.name}`\n"
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += f"{docstring}\n\n"
                        elif isinstance(node, ast.FunctionDef):
                            doc_content += f"## Function `{node.name}`\n"
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += f"{docstring}\n\n"

                    # Create a path-safe filename
                    safe_name = filepath.replace("/", "_").replace("\\", "_") + ".md"

                    if len(doc_content.strip()) > len(
                        f"# Documentation for `{filepath}`\n\n"
                    ):
                        with open(
                            output_dir / safe_name, "w", encoding="utf-8"
                        ) as out_f:
                            out_f.write(doc_content)
                except Exception:  # nosec B110
                    pass


if __name__ == "__main__":
    generate_docs()
