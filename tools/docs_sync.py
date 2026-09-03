import os
import ast
from pathlib import Path

def generate_markdown(file_path: str, rel_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return ""

    md_lines = [f"# Documentation for {rel_path}", ""]

    module_doc = ast.get_docstring(tree)
    if module_doc:
        md_lines.append("## Module Documentation")
        md_lines.append(module_doc)
        md_lines.append("")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            md_lines.append(f"### Class: `{node.name}`")
            class_doc = ast.get_docstring(node)
            if class_doc:
                md_lines.append(class_doc)
            md_lines.append("")

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    md_lines.append(f"#### Method: `{item.name}`")
                    func_doc = ast.get_docstring(item)
                    if func_doc:
                        md_lines.append(func_doc)
                    md_lines.append("")

        elif isinstance(node, ast.FunctionDef):
            md_lines.append(f"### Function: `{node.name}`")
            func_doc = ast.get_docstring(node)
            if func_doc:
                md_lines.append(func_doc)
            md_lines.append("")

    return "\n".join(md_lines)

def main() -> None:
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_api_dir = os.path.join(root_dir, "docs", "api")
    os.makedirs(docs_api_dir, exist_ok=True)

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden directories like .git, .github, .venv
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # Optionally exclude other non-source directories
        dirs[:] = [d for d in dirs if d not in ('docs', 'artifacts', 'dashboard_output', 'node_modules', 'dist', 'build', '__pycache__')]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)

                # Create safe filename using relative path to prevent collisions
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                out_path = os.path.join(docs_api_dir, safe_name)

                md_content = generate_markdown(file_path, rel_path)
                if md_content.strip():
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write(md_content)

    print(f"Documentation generated in {docs_api_dir}")

if __name__ == "__main__":
    main()
