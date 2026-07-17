import os
import ast
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_docstrings_from_file(filepath):
    """Parses a Python file and extracts docstrings for functions and classes."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
    except Exception as e:
        logging.warning(f"Failed to parse {filepath}: {e}")
        return None

    from typing import Dict, Any

    docstrings: Dict[str, Any] = {
        "module": ast.get_docstring(tree),
        "classes": {},
        "functions": {},
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstrings["classes"][node.name] = {
                "docstring": ast.get_docstring(node),
                "methods": {},
            }
            for class_node in ast.iter_child_nodes(node):
                if isinstance(class_node, ast.FunctionDef) or isinstance(
                    class_node, ast.AsyncFunctionDef
                ):
                    docstrings["classes"][node.name]["methods"][class_node.name] = (
                        ast.get_docstring(class_node)
                    )

        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            # We only want top-level functions here
            if getattr(node, "col_offset", 0) == 0:
                docstrings["functions"][node.name] = ast.get_docstring(node)

    return (
        docstrings
        if (docstrings["module"] or docstrings["classes"] or docstrings["functions"])
        else None
    )


def collect_all_docstrings(root_dir, skip_dirs=None):
    """Walks the repository and collects all docstrings."""
    if skip_dirs is None:
        skip_dirs = {
            ".git",
            ".github",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            "dist",
            "build",
            ".mypy_cache",
            ".pytest_cache",
        }

    all_docs = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to skip specific directories
        dirnames[:] = [
            d for d in dirnames if d not in skip_dirs and not d.startswith(".")
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                docs = extract_docstrings_from_file(filepath)
                if docs:
                    all_docs[rel_path] = docs

    return all_docs


def write_api_reference(docs_dict, output_path):
    """Writes the collected docstrings to a Markdown file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# API Reference\n\n")
        f.write(
            "This document is automatically generated from the docstrings in the source code.\n\n"
        )

        for filepath, docs in sorted(docs_dict.items()):
            f.write(f"## `{filepath}`\n\n")

            if docs["module"]:
                f.write(f"**Module Docstring:**\n\n```text\n{docs['module']}\n```\n\n")

            if docs["classes"]:
                f.write("### Classes\n\n")
                for cls_name, cls_info in docs["classes"].items():
                    f.write(f"#### `{cls_name}`\n\n")
                    if cls_info["docstring"]:
                        f.write(f"```text\n{cls_info['docstring']}\n```\n\n")

                    if cls_info["methods"]:
                        for method_name, method_doc in cls_info["methods"].items():
                            if method_doc:
                                f.write(
                                    f"- **`{method_name}()`**: {method_doc.splitlines()[0]}\n"
                                )
                        f.write("\n")

            if docs["functions"]:
                f.write("### Functions\n\n")
                for func_name, func_doc in docs["functions"].items():
                    f.write(f"#### `{func_name}()`\n\n")
                    if func_doc:
                        f.write(f"```text\n{func_doc}\n```\n\n")
            f.write("---\n\n")


if __name__ == "__main__":
    root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(root_directory, "docs")
    api_ref_path = os.path.join(docs_dir, "api_reference.md")

    logging.info(f"Collecting docstrings from {root_directory}...")
    collected_docs = collect_all_docstrings(root_directory)

    logging.info(f"Writing API reference to {api_ref_path}...")
    write_api_reference(collected_docs, api_ref_path)
    logging.info("Documentation sync complete.")
