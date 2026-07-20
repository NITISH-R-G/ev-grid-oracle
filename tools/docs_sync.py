import ast
import os
from typing import List


def extract_docs(root_dir: str) -> List[str]:
    docs: List[str] = ["# API Reference\n"]
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip common non-source directories
        if any(
            d in dirpath
            for d in [
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "__pycache__",
                ".github",
                "docs",
                "assets",
            ]
        ):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    parsed = ast.parse(source)
                    docs.append(f"## File: `{filepath}`\n")
                    for node in parsed.body:
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            docs.append(f"### Class: `{node.name}`\n")
                            if docstring:
                                docs.append(f"{docstring}\n")
                        elif isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            docs.append(f"### Function: `{node.name}`\n")
                            if docstring:
                                docs.append(f"{docstring}\n")
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")
    return docs


if __name__ == "__main__":
    docs = extract_docs(".")
    os.makedirs("docs", exist_ok=True)
    with open("docs/api_reference.md", "w", encoding="utf-8") as f:
        f.write("\n".join(docs))
    print("API documentation synced to docs/api_reference.md")
