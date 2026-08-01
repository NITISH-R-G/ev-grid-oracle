"""
Autonomous Documentation Synchronizer.

This tool statically analyzes the repository to extract docstrings
and generates/updates markdown documentation to prevent documentation drift.
"""

import ast
import os
import sys


def extract_docs(filepath: str) -> str:
    """Extract docstrings from a python file to markdown format."""
    docs = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read {filepath}: {e}", file=sys.stderr)
        return ""

    try:
        tree = ast.parse(content, filename=filepath)
    except SyntaxError as e:
        print(f"Syntax error in {filepath}: {e}", file=sys.stderr)
        return ""

    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(f"# {os.path.basename(filepath)}\n\n{module_doc}\n")
    else:
        docs.append(f"# {os.path.basename(filepath)}\n")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docs.append(f"## Class: `{node.name}`\n")
            docstring = ast.get_docstring(node)
            if docstring:
                docs.append(f"{docstring}\n")

            for subnode in node.body:
                if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    docs.append(f"### Method: `{subnode.name}`\n")
                    method_doc = ast.get_docstring(subnode)
                    if method_doc:
                        docs.append(f"{method_doc}\n")

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docs.append(f"## Function: `{node.name}`\n")
            docstring = ast.get_docstring(node)
            if docstring:
                docs.append(f"{docstring}\n")

    return "\n".join(docs)


def main() -> None:
    """Main execution."""
    exclude_dirs = {
        "venv",
        "__pycache__",
        "node_modules",
        "dashboard_output",
    }
    output_dir = os.path.join("docs", "api")
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)

                # Skip the tools directory for API docs to reduce noise
                if "tools" in root:
                    continue

                # Normalize path and create safe filename
                filepath = os.path.normpath(filepath)
                safe_name = filepath.replace(os.sep, "_").replace(".py", ".md")

                doc_content = extract_docs(filepath)
                if doc_content.strip() != f"# {os.path.basename(filepath)}":
                    output_path = os.path.join(output_dir, safe_name)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(doc_content)

    print(f"Successfully synchronized documentation to {output_dir}")


if __name__ == "__main__":
    main()
