import ast
import os
import pathlib

def extract_docstrings(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
    except Exception:
        return ""

    docs = []

    # Module docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(f"## Module: {filepath}\n\n{module_doc}\n")
    else:
        docs.append(f"## Module: {filepath}\n")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            docs.append(f"### Class: `{node.name}`\n")
            cls_doc = ast.get_docstring(node)
            if cls_doc:
                docs.append(f"{cls_doc}\n")
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    docs.append(f"#### Method: `{subnode.name}`\n")
                    func_doc = ast.get_docstring(subnode)
                    if func_doc:
                        docs.append(f"{func_doc}\n")
        elif isinstance(node, ast.FunctionDef):
            docs.append(f"### Function: `{node.name}`\n")
            func_doc = ast.get_docstring(node)
            if func_doc:
                docs.append(f"{func_doc}\n")

    return "\n".join(docs)

def sync_docs():
    root = pathlib.Path(".")
    docs_dir = pathlib.Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root):
        # Ignore hidden directories like .git
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        # Skip node_modules, build directories, etc.
        if "node_modules" in dirpath or "dist" in dirpath or "venv" in dirpath:
            continue

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)

                # generate safe name: replace slashes with underscores
                safe_name = filepath.replace("/", "_").replace("\\", "_").replace(".py", ".md")
                out_path = docs_dir / safe_name

                doc_content = extract_docstrings(filepath)
                if doc_content.strip():
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write(doc_content)

if __name__ == "__main__":
    sync_docs()
    print("Documentation synced successfully.")
