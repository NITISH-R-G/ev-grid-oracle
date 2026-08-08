import logging

logger = logging.getLogger(__name__)
import ast
import os


def generate_docs(root_dir: str) -> str:
    """
    Parses Python files using `ast` and generates API documentation in Markdown.
    Properly ignores hidden directories.
    """
    docs = "# API Documentation\n\n"

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Ignore specific build artifacts and dependencies
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in [
                "build",
                "node_modules",
                "dist",
                "dist-ssr",
                "venv",
                "__pycache__",
                "artifacts",
            ]
        ]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                has_content = False

                file_docs = f"## Module: `{filepath}`\n\n"

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        has_content = True
                        file_docs += f"### Class: `{node.name}`\n"
                        docstring = ast.get_docstring(node)
                        if docstring:
                            file_docs += f"> {docstring}\n\n"
                        else:
                            file_docs += "_No docstring available._\n\n"
                    elif isinstance(node, ast.FunctionDef) and not isinstance(
                        node, ast.AsyncFunctionDef
                    ):  # Keeping it simple, can add async if needed
                        # Only document top-level functions or methods might be complicated with simple walk.
                        # ast.walk visits all nodes, so methods are included but without class context in simple print.
                        # Let's just output them.
                        has_content = True
                        file_docs += f"### Function: `{node.name}`\n"
                        docstring = ast.get_docstring(node)
                        if docstring:
                            file_docs += f"> {docstring}\n\n"
                        else:
                            file_docs += "_No docstring available._\n\n"
                    elif isinstance(node, ast.AsyncFunctionDef):
                        has_content = True
                        file_docs += f"### Async Function: `{node.name}`\n"
                        docstring = ast.get_docstring(node)
                        if docstring:
                            file_docs += f"> {docstring}\n\n"
                        else:
                            file_docs += "_No docstring available._\n\n"

                if has_content:
                    docs += file_docs

            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to parse {filepath}: {e}")
                continue  # nosec B112


    return docs


if __name__ == "__main__":
    docs_content = generate_docs(".")
    os.makedirs("docs", exist_ok=True)
    with open("docs/api_reference.md", "w", encoding="utf-8") as f:
        f.write(docs_content)
    print("API documentation generated at docs/api_reference.md")
