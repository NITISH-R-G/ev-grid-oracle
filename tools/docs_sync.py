#!/usr/bin/env python3
"""
Autonomous Documentation Synchronizer
Generates markdown documentation files dynamically from source file docstrings
to keep documentation in sync with codebase reality.
"""

import ast
import os
from pathlib import Path


def generate_docs(root_dir: str, output_dir: str) -> None:
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Explicitly ignore hidden directories and excluded folders
        dirnames[:] = [
            d
            for d in dirnames
            if not d.startswith(".")
            and d not in ("venv", "node_modules", "artifacts", "docs")
        ]

        for file in filenames:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue  # nosec B112

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            module_doc = ast.get_docstring(tree)
            if not module_doc:
                # Skip files without module-level docstrings
                continue

            rel_path = os.path.relpath(filepath, root_dir)
            # Create a path-safe filename to prevent namespace collisions
            safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
            out_file = os.path.join(output_dir, safe_name)

            with open(out_file, "w", encoding="utf-8") as out:
                out.write(f"# {rel_path}\n\n")
                out.write(f"## Module Docstring\n\n{module_doc}\n\n")

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        cls_doc = ast.get_docstring(node)
                        out.write(f"### Class: {node.name}\n\n")
                        if cls_doc:
                            out.write(f"{cls_doc}\n\n")
                    elif isinstance(node, ast.FunctionDef):
                        func_doc = ast.get_docstring(node)
                        out.write(f"### Function: {node.name}\n\n")
                        if func_doc:
                            out.write(f"{func_doc}\n\n")


def main() -> None:
    root_dir = Path(__file__).parent.parent
    docs_api_dir = root_dir / "docs" / "api"
    docs_api_dir.mkdir(parents=True, exist_ok=True)

    generate_docs(str(root_dir), str(docs_api_dir))
    print(f"Documentation synchronized in {docs_api_dir}")


if __name__ == "__main__":
    main()
