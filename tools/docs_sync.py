import ast
import os
from typing import List, Dict, Optional


def extract_docstrings(filepath: str) -> List[Dict[str, Optional[str]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return []

    docs: List[Dict[str, Optional[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node)
            if doc:
                docs.append(
                    {"name": node.name, "type": type(node).__name__, "docstring": doc}
                )
    return docs


def sync_docs(root_dir: str = ".", output_dir: str = "docs/api") -> None:
    os.makedirs(output_dir, exist_ok=True)

    for subdir, _, files in os.walk(root_dir):
        if any(
            ignored in subdir
            for ignored in [".venv", "node_modules", "__pycache__", "build", "docs"]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(subdir, file)
                docs = extract_docstrings(filepath)
                if docs:
                    # Generate a markdown file
                    safe_name = filepath.replace("/", "_").replace("\\", "_") + ".md"
                    out_path = os.path.join(output_dir, safe_name)
                    with open(out_path, "w", encoding="utf-8") as out:
                        out.write(f"# API Documentation for `{filepath}`\n\n")
                        for d in docs:
                            out.write(f"## {d['type']}: {d['name']}\n")
                            out.write(f"```text\n{d['docstring']}\n```\n\n")


if __name__ == "__main__":
    sync_docs()
    print("Documentation synced successfully to docs/api/")
