import ast
import os


def extract_docstrings(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except SyntaxError:
            return ""

    docs = []

    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(f"## Module: {os.path.basename(filepath)}")
        docs.append(module_doc)
        docs.append("")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            if docstring:
                docs.append(f"### Class: {node.name}")
                docs.append(docstring)
                docs.append("")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            if docstring:
                docs.append(f"#### Function: {node.name}")
                docs.append(docstring)
                docs.append("")

    return "\n".join(docs)


def sync_docs(root_dir: str = "."):
    output_dir = os.path.join(root_dir, "docs", "api")
    os.makedirs(output_dir, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                docs = extract_docstrings(filepath)
                if docs.strip():
                    safe_filename = rel_path.replace(os.sep, "_").replace(".py", ".md")
                    out_path = os.path.join(output_dir, safe_filename)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(docs)


if __name__ == "__main__":
    sync_docs()
    print("Documentation sync complete.")
