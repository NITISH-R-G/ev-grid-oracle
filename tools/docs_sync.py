import ast
import os
import sys

def sync_docs(root_dir: str = ".", out_dir: str = "docs/api") -> None:
    os.makedirs(out_dir, exist_ok=True)

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories robustly
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # Also ignore some common non-source directories
        dirs[:] = [d for d in dirs if d not in ('node_modules', 'artifacts', 'docs', 'dashboard_output', 'web')]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                print(f"Failed to read {filepath}: {e}", file=sys.stderr)
                continue

            try:
                tree = ast.parse(content, filename=filepath)
            except Exception as e:
                print(f"Failed to parse {filepath}: {e}", file=sys.stderr)
                continue

            doc_content = []

            module_doc = ast.get_docstring(tree)
            if module_doc:
                doc_content.append(f"# Module: `{filepath}`\n\n{module_doc}\n")

            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_doc = ast.get_docstring(node)
                    doc_content.append(f"## Class: `{node.name}`\n")
                    if class_doc:
                        doc_content.append(f"{class_doc}\n")

                    for subnode in node.body:
                        if isinstance(subnode, ast.FunctionDef) or isinstance(subnode, ast.AsyncFunctionDef):
                            func_doc = ast.get_docstring(subnode)
                            doc_content.append(f"### Method: `{subnode.name}`\n")
                            if func_doc:
                                doc_content.append(f"{func_doc}\n")

                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    func_doc = ast.get_docstring(node)
                    doc_content.append(f"## Function: `{node.name}`\n")
                    if func_doc:
                        doc_content.append(f"{func_doc}\n")

            if doc_content:
                safe_name = filepath.replace(os.sep, "_").replace(".py", ".md")
                if safe_name.startswith("._"):
                    safe_name = safe_name[2:]
                out_path = os.path.join(out_dir, safe_name)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(doc_content))

if __name__ == "__main__":
    sync_docs()
    print("Documentation synced successfully.")
