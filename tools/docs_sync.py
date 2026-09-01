#!/usr/bin/env python3
"""
Autonomous Documentation Synchronizer.
Parses Python source files in the repository using the `ast` module,
extracts classes, functions, and docstrings, and generates Markdown
files in the `docs/api/` directory. Constructing path-safe filenames
incorporating the relative directory path to prevent namespace collisions.
"""

import ast
import os
import sys


def generate_docs(repo_root: str):
    docs_dir = os.path.join(repo_root, "docs", "api")
    os.makedirs(docs_dir, exist_ok=True)

    for root_dir, dirs, files in os.walk(repo_root):
        if (
            ".git" in root_dir
            or "node_modules" in root_dir
            or ".venv" in root_dir
            or "venv" in root_dir
        ):
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root_dir, file)
            rel_path = os.path.relpath(filepath, repo_root)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read(), filename=filepath)
            except Exception as e:  # noqa: BLE001
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

            doc_lines = [f"# API Documentation for `{rel_path}`", ""]
            module_doc = ast.get_docstring(tree)
            if module_doc:
                doc_lines.append("## Module Description")
                doc_lines.append(module_doc)
                doc_lines.append("")

            has_content = False
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    has_content = True
                    doc_lines.append(f"## Class `{node.name}`")
                    cls_doc = ast.get_docstring(node)
                    if cls_doc:
                        doc_lines.append(cls_doc)
                    doc_lines.append("")
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            doc_lines.append(f"### Method `{item.name}`")
                            func_doc = ast.get_docstring(item)
                            if func_doc:
                                doc_lines.append(func_doc)
                            doc_lines.append("")
                elif isinstance(node, ast.FunctionDef):
                    has_content = True
                    doc_lines.append(f"## Function `{node.name}`")
                    func_doc = ast.get_docstring(node)
                    if func_doc:
                        doc_lines.append(func_doc)
                    doc_lines.append("")

            if has_content or module_doc:
                # Create a path-safe filename
                safe_name = (
                    rel_path.replace(os.sep, "_")
                    .replace("/", "_")
                    .replace(".py", ".md")
                )
                out_path = os.path.join(docs_dir, safe_name)
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write("\n".join(doc_lines))


if __name__ == "__main__":
    generate_docs(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
