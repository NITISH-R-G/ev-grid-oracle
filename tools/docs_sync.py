#!/usr/bin/env python3
import ast
import json
import os
from typing import Any


def sync_docs() -> None:
    docs: dict[str, Any] = {}

    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".github" in dirs:
            dirs.remove(".github")
        if "venv" in dirs:
            dirs.remove("venv")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if "node_modules" in dirs:
            dirs.remove("node_modules")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    file_docs: list[dict[str, Any]] = []

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                file_docs.append(
                                    {
                                        "type": "class"
                                        if isinstance(node, ast.ClassDef)
                                        else "function",
                                        "name": node.name,
                                        "docstring": docstring,
                                    }
                                )

                    if file_docs:
                        docs[filepath] = file_docs

                except Exception as e:  # noqa: BLE001
                    print(f"Failed to parse {filepath}: {e}")

    os.makedirs("docs", exist_ok=True)
    with open("docs/api_reference.json", "w", encoding="utf-8") as out:
        json.dump(docs, out, indent=2)


if __name__ == "__main__":
    sync_docs()
