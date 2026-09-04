import ast
import os


def docs_sync() -> None:
    os.makedirs("docs/api", exist_ok=True)
    for root, dirs, files in os.walk("."):
        if ".git" in root or ".venv" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)

                    doc_content = f"# {filepath}\n\n"
                    has_content = False

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                            doc_content += f"## {node.name}\n\n"
                            if ast.get_docstring(node):
                                doc_content += f"{ast.get_docstring(node)}\n\n"
                            has_content = True

                    if has_content:
                        safe_name = filepath.replace("/", "_").replace("\\", "_")
                        with open(
                            f"docs/api/{safe_name}.md", "w", encoding="utf-8"
                        ) as out:
                            out.write(doc_content)
                except Exception:  # noqa: BLE001, S110
                    pass


if __name__ == "__main__":
    docs_sync()
