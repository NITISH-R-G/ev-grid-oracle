import ast
import os
from typing import Any


def parse_file_for_docs(filepath: str) -> dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {"classes": [], "functions": [], "module_doc": None}

    module_doc = ast.get_docstring(tree)
    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({"name": node.name, "doc": ast.get_docstring(node)})
        elif isinstance(node, ast.FunctionDef):
            functions.append({"name": node.name, "doc": ast.get_docstring(node)})

    return {"module_doc": module_doc, "classes": classes, "functions": functions}


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(repo_root, "docs", "api")
    os.makedirs(output_dir, exist_ok=True)

    for root, dnames, fnames in os.walk(repo_root):
        dnames[:] = [d for d in dnames if not d.startswith(".")]

        # Avoid traversing into virtual environments or node_modules
        if any(
            ignored in root
            for ignored in ["venv", "node_modules", "web/dist", "artifacts"]
        ):
            continue

        for fname in fnames:
            if fname.endswith(".py"):
                filepath = os.path.join(root, fname)
                rel_path = os.path.relpath(filepath, repo_root)
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                output_path = os.path.join(output_dir, safe_name)

                docs_info = parse_file_for_docs(filepath)
                if (
                    not docs_info["classes"]
                    and not docs_info["functions"]
                    and not docs_info["module_doc"]
                ):
                    continue

                with open(output_path, "w", encoding="utf-8") as out_f:
                    out_f.write(f"# Documentation for `{rel_path}`\n\n")
                    if docs_info["module_doc"]:
                        out_f.write(
                            f"## Module Overview\n{docs_info['module_doc']}\n\n"
                        )

                    if docs_info["classes"]:
                        out_f.write("## Classes\n")
                        for cls in docs_info["classes"]:
                            out_f.write(f"### `{cls['name']}`\n")
                            if cls["doc"]:
                                out_f.write(f"{cls['doc']}\n\n")
                            else:
                                out_f.write("*(No docstring provided)*\n\n")

                    if docs_info["functions"]:
                        out_f.write("## Functions\n")
                        for func in docs_info["functions"]:
                            out_f.write(f"### `{func['name']}`\n")
                            if func["doc"]:
                                out_f.write(f"{func['doc']}\n\n")
                            else:
                                out_f.write("*(No docstring provided)*\n\n")
    print(f"Documentation generated in {output_dir}")


if __name__ == "__main__":
    main()
