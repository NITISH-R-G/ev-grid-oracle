import ast
import os
from pathlib import Path


def generate_docs(repo_path="."):
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in ("artifacts", "node_modules", "dist", "build", "__pycache__", "docs")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=filepath)

                # Construct path-safe filename based on relative path
                rel_path = os.path.relpath(filepath, repo_path)
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                out_path = docs_dir / safe_name

                doc_lines = [f"# API Documentation for `{rel_path}`\n"]

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        doc_lines.append(f"## Class: `{node.name}`")
                        docstring = ast.get_docstring(node)
                        if docstring:
                            doc_lines.append(f"```text\n{docstring}\n```")
                        doc_lines.append("")
                    elif isinstance(node, ast.FunctionDef):
                        doc_lines.append(f"### Function: `{node.name}`")
                        docstring = ast.get_docstring(node)
                        if docstring:
                            doc_lines.append(f"```text\n{docstring}\n```")
                        doc_lines.append("")

                if (
                    len(doc_lines) > 1
                ):  # Only write if there's actual content (classes/funcs)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write("\n".join(doc_lines))

            except Exception as e:
                print(f"Failed to process {filepath}: {e}")


if __name__ == "__main__":
    generate_docs()
    print("API documentation generated in docs/api/")
