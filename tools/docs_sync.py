import os
import ast


def generate_docs():
    output_dir = "docs/api"
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        if any(
            root.startswith(f"./{d}") or root == f"./{d}"
            for d in [
                ".git",
                ".github",
                ".venv",
                "venv",
                "node_modules",
                "web",
                "docs",
                "artifacts",
                ".pytest_cache",
                ".ruff_cache",
                "__pycache__",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    doc_lines = []
                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        doc_lines.append(f"# {filepath}\n")
                        doc_lines.append(f"{module_doc}\n")

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc_lines.append(f"## Class: `{node.name}`\n")
                            cls_doc = ast.get_docstring(node)
                            if cls_doc:
                                doc_lines.append(f"{cls_doc}\n")
                        elif isinstance(node, ast.FunctionDef) or isinstance(
                            node, ast.AsyncFunctionDef
                        ):
                            doc_lines.append(f"### Function: `{node.name}`\n")
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                doc_lines.append(f"{func_doc}\n")

                    if doc_lines:
                        # Construct safe filename
                        safe_name = (
                            filepath.replace("./", "")
                            .replace("/", "_")
                            .replace(".py", ".md")
                        )
                        out_path = os.path.join(output_dir, safe_name)
                        with open(out_path, "w", encoding="utf-8") as out_f:
                            out_f.write("\n".join(doc_lines))
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")


if __name__ == "__main__":
    generate_docs()
