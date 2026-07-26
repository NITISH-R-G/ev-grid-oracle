import ast
import os
from typing import Any, Dict, List


def extract_docstrings(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return []

    docs: List[Dict[str, Any]] = []

    # Get module level docstring
    module_doc = ast.get_docstring(tree)
    if module_doc:
        docs.append(
            {"type": "module", "name": os.path.basename(filepath), "doc": module_doc}
        )

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            cls_doc = ast.get_docstring(node)
            if cls_doc:
                docs.append({"type": "class", "name": node.name, "doc": cls_doc})
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    func_doc = ast.get_docstring(subnode)
                    if func_doc:
                        docs.append(
                            {
                                "type": "method",
                                "name": f"{node.name}.{subnode.name}",
                                "doc": func_doc,
                            }
                        )
        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node)
            if func_doc:
                docs.append({"type": "function", "name": node.name, "doc": func_doc})

    return docs


def generate_api_docs(src_dir: str, out_file: str) -> None:
    api_docs = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                docs = extract_docstrings(filepath)
                if docs:
                    api_docs.append(f"## `{filepath}`\n")
                    for doc in docs:
                        api_docs.append(
                            f"### {doc['type'].capitalize()}: {doc['name']}"
                        )
                        api_docs.append(f"{doc['doc']}\n")

    if api_docs:
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("# API Documentation\n\n" + "\n".join(api_docs))


if __name__ == "__main__":
    generate_api_docs("ev_grid_oracle", "docs/api/ev_grid_oracle.md")
    generate_api_docs("server", "docs/api/server.md")
