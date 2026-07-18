import os
import ast


def generate_docs(repo_path: str = ".") -> str:
    markdown = "# API Reference\n\nThis file is auto-generated.\n\n"

    for root, dirs, files in os.walk(repo_path):
        if any(
            ignored in root
            for ignored in [
                ".venv",
                "venv",
                ".git",
                "node_modules",
                "artifacts",
                "dashboard_output",
            ]
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    tree = ast.parse(content)

                    file_has_docs = False
                    file_markdown = f"## `{filepath}`\n\n"

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                file_has_docs = True
                                file_markdown += (
                                    f"### Class `{node.name}`\n\n{docstring}\n\n"
                                )

                        elif isinstance(node, ast.FunctionDef):
                            docstring = ast.get_docstring(node)
                            if docstring:
                                file_has_docs = True
                                file_markdown += (
                                    f"### Function `{node.name}()`\n\n{docstring}\n\n"
                                )

                    if file_has_docs:
                        markdown += file_markdown

                except Exception as e:
                    print(f"Error parsing {filepath} for docs: {e}")

    return markdown


if __name__ == "__main__":
    docs = generate_docs()

    os.makedirs("docs", exist_ok=True)
    with open("docs/api_reference.md", "w", encoding="utf-8") as f:
        f.write(docs)
    print("API documentation generated at docs/api_reference.md")
