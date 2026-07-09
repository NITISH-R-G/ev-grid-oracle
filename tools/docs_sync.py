import os
import ast
import re


def extract_api_info():
    api_info = "## Auto-Generated API Reference\n\n"
    for root, _, files in os.walk("."):
        if ".venv" in root or ".git" in root or "node_modules" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)
                    file_info = ""
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            file_info += f"### Class `{node.name}`\n"
                            docstring = ast.get_docstring(node)
                            if docstring:
                                file_info += f"{docstring}\n\n"
                        elif isinstance(node, ast.FunctionDef):
                            file_info += f"### Function `{node.name}`\n"
                            docstring = ast.get_docstring(node)
                            if docstring:
                                file_info += f"{docstring}\n\n"

                    if file_info:
                        api_info += f"### {filepath}\n\n{file_info}"
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")
    return api_info


def update_readme(api_info):
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for existing API section to replace
    pattern = re.compile(r"## Auto-Generated API Reference.*?(?=## |$)", re.DOTALL)
    if pattern.search(content):
        new_content = pattern.sub(api_info, content)
    else:
        new_content = content + "\n" + api_info

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    api_info = extract_api_info()
    update_readme(api_info)
