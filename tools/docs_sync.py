import os
import ast


def extract_docstrings(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception:
            return ""

    docs = []
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(f"# Module: {filepath}\n\n{module_doc}\n")

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            if doc:
                docs.append(f"## Class: {node.name}\n\n{doc}\n")
        elif isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node)
            if doc:
                docs.append(f"### Function: {node.name}\n\n{doc}\n")

    return "\n".join(docs)


def sync_docs():
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                docs = extract_docstrings(filepath)
                if docs:
                    safe_name = (
                        filepath.replace("./", "")
                        .replace("/", "_")
                        .replace(".py", ".md")
                    )
                    out_path = os.path.join("docs/api", safe_name)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(docs)


if __name__ == "__main__":
    sync_docs()
