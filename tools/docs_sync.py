#!/usr/bin/env python3
"""Autonomous documentation generator."""

import ast
import os
from pathlib import Path


def generate_docs(repo_root: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(repo_root):
        # Explicitly skip hidden directories like .git, .github, .venv, etc.
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = Path(root) / file
            rel_path = filepath.relative_to(repo_root)

            # Simple heuristic: ignore files with test in their names or in test dirs
            if "test" in str(rel_path).lower():
                continue

            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                module = ast.parse(content)
                docstring = ast.get_docstring(module)

                # If there's no docstring and no classes/functions, skip
                classes = [n for n in module.body if isinstance(n, ast.ClassDef)]
                functions = [n for n in module.body if isinstance(n, ast.FunctionDef)]

                if not docstring and not classes and not functions:
                    continue

                # Construct safe output filename using underscores instead of slashes
                out_name = str(rel_path).replace("/", "_").replace(".py", ".md")
                out_path = output_dir / out_name

                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(f"# `{rel_path}`\n\n")
                    if docstring:
                        out_f.write(f"## Module Description\n\n{docstring}\n\n")

                    if classes:
                        out_f.write("## Classes\n\n")
                        for cls in classes:
                            cls_doc = ast.get_docstring(cls)
                            out_f.write(f"### `{cls.name}`\n")
                            if cls_doc:
                                out_f.write(f"{cls_doc}\n")
                            out_f.write("\n")

                    if functions:
                        out_f.write("## Functions\n\n")
                        for func in functions:
                            func_doc = ast.get_docstring(func)
                            out_f.write(f"### `{func.name}`\n")
                            if func_doc:
                                out_f.write(f"{func_doc}\n")
                            out_f.write("\n")

            except Exception as e:
                print(f"Failed to process {filepath}: {e}")


if __name__ == "__main__":
    root = Path.cwd()
    docs_out = root / "docs" / "api"
    generate_docs(root, docs_out)
    print(f"Successfully synced docs to {docs_out}")
