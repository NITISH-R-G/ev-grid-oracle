import ast
import os


def generate_docs() -> None:
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in [
                "venv",
                "node_modules",
                "dashboard_output",
                "artifacts",
                "docs",
                "web",
            ]
        ]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue

                doc_content = f"# API Reference for {filepath}\n\n"

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        doc_content += f"## Class {node.name}\n"
                        docstring = ast.get_docstring(node)
                        if docstring:
                            doc_content += f"{docstring}\n\n"
                    elif isinstance(node, ast.FunctionDef):
                        doc_content += f"### Function {node.name}\n"
                        docstring = ast.get_docstring(node)
                        if docstring:
                            doc_content += f"{docstring}\n\n"

                safe_name = (
                    filepath.replace("./", "").replace("/", "_").replace(".py", ".md")
                )
                with open(f"docs/api/{safe_name}", "w", encoding="utf-8") as f:
                    f.write(doc_content)


if __name__ == "__main__":
    generate_docs()
