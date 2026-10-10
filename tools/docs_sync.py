import ast
import os
from pathlib import Path


def generate_docs():
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)

    root_dir = Path(".")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories (e.g. .git, .github, .venv)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Ignore common build/test directories
        if any(
            ignored in dirpath
            for ignored in [
                "node_modules",
                "__pycache__",
                "dist",
                "build",
                "artifacts",
                "docs",
            ]
        ):
            continue

        for file in filenames:
            if file.endswith(".py"):
                file_path = Path(dirpath) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    doc_content = f"# {file_path}\n\n"
                    has_content = False

                    for node in tree.body:
                        if isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += (
                                    f"## Function: `{node.name}`\n\n{docstring}\n\n"
                                )
                                has_content = True
                            else:
                                doc_content += f"## Function: `{node.name}`\n\nNo docstring provided.\n\n"
                                has_content = True
                        elif isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                doc_content += (
                                    f"## Class: `{node.name}`\n\n{docstring}\n\n"
                                )
                                has_content = True
                            else:
                                doc_content += f"## Class: `{node.name}`\n\nNo docstring provided.\n\n"
                                has_content = True

                    if has_content:
                        # Construct a path-safe filename
                        safe_name = str(file_path).replace("/", "_").replace("\\", "_")
                        out_path = docs_dir / f"{safe_name}.md"
                        with open(out_path, "w", encoding="utf-8") as out_f:
                            out_f.write(doc_content)

                except Exception as e:  # noqa: BLE001
                    print(f"Failed to process {file_path}: {e}")


if __name__ == "__main__":
    generate_docs()
