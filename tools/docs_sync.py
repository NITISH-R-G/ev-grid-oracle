import ast
import os
from pathlib import Path


def generate_markdown(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return f"# Error parsing {file_path.name}\n\nCould not parse this file as Python code."

    module_docstring = ast.get_docstring(tree)

    md = [f"# Module: `{file_path.name}`\n"]
    if module_docstring:
        md.append(f"{module_docstring}\n")

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            md.append(f"## Class: `{node.name}`")
            class_doc = ast.get_docstring(node)
            if class_doc:
                md.append(f"\n{class_doc}\n")

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    md.append(f"### Method: `{item.name}`")
                    method_doc = ast.get_docstring(item)
                    if method_doc:
                        md.append(f"\n{method_doc}\n")

        elif isinstance(node, ast.FunctionDef):
            md.append(f"## Function: `{node.name}`")
            func_doc = ast.get_docstring(node)
            if func_doc:
                md.append(f"\n{func_doc}\n")

    return "\n".join(md)


def main():
    root_dir = Path(".")
    docs_api_dir = root_dir / "docs" / "api"
    docs_api_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Explicitly ignore standard virtual env or build folders
        ignore_dirs = ["venv", "build", "dist", "node_modules"]
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(root_dir)

                # Construct path-safe filename incorporating relative path
                safe_name = str(rel_path).replace(os.sep, "_").replace(".py", ".md")
                out_path = docs_api_dir / safe_name

                markdown_content = generate_markdown(file_path)
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(markdown_content)

    print(f"Generated API documentation in {docs_api_dir}")


if __name__ == "__main__":
    main()
