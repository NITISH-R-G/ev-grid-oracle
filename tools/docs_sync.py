import ast
import os


def generate_markdown_docs(filepath: str, root_dir: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content, filename=filepath)
        except Exception:
            return ""

    rel_path = os.path.relpath(filepath, root_dir)
    doc_lines = [f"# {rel_path}", ""]

    module_doc = ast.get_docstring(tree)
    if module_doc:
        doc_lines.extend([module_doc, ""])

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc_lines.extend([f"## Class `{node.name}`", ""])
            class_doc = ast.get_docstring(node)
            if class_doc:
                doc_lines.extend([class_doc, ""])
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(
                    item, ast.AsyncFunctionDef
                ):
                    doc_lines.extend([f"### Method `{item.name}`", ""])
                    method_doc = ast.get_docstring(item)
                    if method_doc:
                        doc_lines.extend([method_doc, ""])
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            # Only document top-level functions
            if hasattr(node, "parent") and isinstance(node.parent, ast.ClassDef):
                continue
            doc_lines.extend([f"## Function `{node.name}`", ""])
            func_doc = ast.get_docstring(node)
            if func_doc:
                doc_lines.extend([func_doc, ""])

    if len(doc_lines) <= 2:
        return ""

    return "\n".join(doc_lines)


def sync_docs(root_dir: str):
    docs_dir = os.path.join(root_dir, "docs", "api")
    os.makedirs(docs_dir, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude common directories
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in [
                ".git",
                ".venv",
                "venv",
                "node_modules",
                "__pycache__",
                "build",
                "dist",
                "docs",
            ]
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                markdown_content = generate_markdown_docs(filepath, root_dir)
                if markdown_content:
                    rel_path = os.path.relpath(filepath, root_dir)
                    md_filename = rel_path.replace(os.sep, "_").replace(".py", ".md")
                    out_path = os.path.join(docs_dir, md_filename)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
    print(f"Documentation synced to {docs_dir}")


if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    sync_docs(root)
