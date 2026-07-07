import ast
from pathlib import Path


def extract_docstrings(filepath: Path) -> str:
    """Extracts module, class, and function docstrings from a python file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
    except Exception:
        return ""

    docs = []
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(f"### Module: {filepath.name}\n{module_doc}\n")

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node)
            if class_doc:
                docs.append(f"#### Class: {node.name}\n{class_doc}\n")
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    func_doc = ast.get_docstring(item)
                    if func_doc:
                        docs.append(
                            f"##### Method: {node.name}.{item.name}\n{func_doc}\n"
                        )
        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node)
            if func_doc:
                docs.append(f"#### Function: {node.name}\n{func_doc}\n")

    return "\n".join(docs)


def sync_docs():
    """Syncs basic documentation and extracts API docs."""
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(exist_ok=True)

    # 1. Sync README
    readme_path = repo_root / "README.md"
    sync_target = docs_dir / "index.md"

    if readme_path.exists():
        with open(readme_path, "r") as f:
            content = f.read()

        with open(sync_target, "w") as f:
            f.write(content)

    # 2. Extract API Documentation from server and ev_grid_oracle
    api_docs = ["# API Documentation\n\nAutomatically generated from source code.\n"]

    for folder in ["server", "ev_grid_oracle"]:
        folder_path = repo_root / folder
        if not folder_path.exists():
            continue

        for py_file in folder_path.rglob("*.py"):
            doc_content = extract_docstrings(py_file)
            if doc_content:
                api_docs.append(f"## {py_file.relative_to(repo_root)}\n\n{doc_content}")

    api_target = docs_dir / "api_reference.md"
    with open(api_target, "w") as f:
        f.write("\n".join(api_docs))

    print("Documentation synchronized. API Reference generated.")


if __name__ == "__main__":
    sync_docs()
