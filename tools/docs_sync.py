import ast
import os
from typing import Any


def extract_docs(filepath: str) -> dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return {"classes": [], "functions": []}

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "No docstring available.",
                    "lineno": node.lineno,
                }
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Exclude private/dunder methods unless they are __init__
            if node.name.startswith("_") and node.name != "__init__":
                continue
            functions.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node) or "No docstring available.",
                    "lineno": node.lineno,
                }
            )

    return {"classes": classes, "functions": functions}


def generate_markdown(filepath: str, docs: dict[str, Any]) -> str:
    md = f"# API Documentation for `{filepath}`\n\n"

    if docs["classes"]:
        md += "## Classes\n\n"
        for c in docs["classes"]:
            md += f"### `{c['name']}`\n\n"
            md += f"**Line**: {c['lineno']}\n\n"
            md += f"{c['docstring']}\n\n"

    if docs["functions"]:
        md += "## Functions\n\n"
        for f in docs["functions"]:
            md += f"### `{f['name']}`\n\n"
            md += f"**Line**: {f['lineno']}\n\n"
            md += f"{f['docstring']}\n\n"

    return md


def main():
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        if ".git" in root or ".venv" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.normpath(os.path.join(root, file))
                docs = extract_docs(filepath)

                if docs["classes"] or docs["functions"]:
                    md = generate_markdown(filepath, docs)

                    # Create a path-safe filename based on the original path
                    safe_name = filepath.replace(os.sep, "_").replace(".py", ".md")
                    safe_name = safe_name.removeprefix("._")

                    out_path = os.path.join("docs", "api", safe_name)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(md)


if __name__ == "__main__":
    main()
