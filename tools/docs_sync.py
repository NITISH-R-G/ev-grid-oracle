import ast
import os
from typing import Any

def extract_docs(filepath: str) -> dict[str, list[dict[str, Any]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception: # noqa: BLE001
            return {"classes": [], "functions": []}

    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node) or "No docstring provided."
            classes.append({
                "name": node.name,
                "docstring": docstring
            })
        elif isinstance(node, ast.FunctionDef):
            docstring = ast.get_docstring(node) or "No docstring provided."
            functions.append({
                "name": node.name,
                "docstring": docstring
            })

    return {"classes": classes, "functions": functions}

def main() -> None:
    output_dir = "docs/api"
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden system directories correctly to prevent .git/.venv traversal
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if "node_modules" in root or "artifacts" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                docs = extract_docs(filepath)

                if not docs["classes"] and not docs["functions"]:
                    continue

                # Construct a path-safe filename based on relative directory path
                rel_path = os.path.relpath(filepath, ".")
                safe_name = rel_path.replace(os.path.sep, "_").replace(".py", ".md")
                out_path = os.path.join(output_dir, safe_name)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(f"# Documentation for `{rel_path}`\n\n")
                    if docs["classes"]:
                        f.write("## Classes\n\n")
                        for cls in docs["classes"]:
                            f.write(f"### `{cls['name']}`\n\n{cls['docstring']}\n\n")
                    if docs["functions"]:
                        f.write("## Functions\n\n")
                        for func in docs["functions"]:
                            f.write(f"### `{func['name']}`\n\n{func['docstring']}\n\n")

if __name__ == "__main__":
    main()
