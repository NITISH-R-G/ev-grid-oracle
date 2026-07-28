import os
import ast
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_file_for_docs(filepath: str) -> str:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except Exception as e:
        logging.warning(f"Could not read {filepath}: {e}")
        return ""

    try:
        tree = ast.parse(source)
    except Exception as e:
        logging.warning(f"Could not parse {filepath}: {e}")
        return ""

    content = f"## {filepath}\n\n"

    module_doc = ast.get_docstring(tree)
    if module_doc:
        content += f"{module_doc}\n\n"

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            content += f"### Class: `{node.name}`\n\n"
            doc = ast.get_docstring(node)
            if doc:
                content += f"{doc}\n\n"
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            # Only document top-level functions or public methods (simplified)
            if not node.name.startswith("_"):
                content += f"### Function: `{node.name}`\n\n"
                doc = ast.get_docstring(node)
                if doc:
                    content += f"{doc}\n\n"

    return content


def main() -> None:
    docs_content = "# API Reference\n\nThis is an auto-generated API reference.\n\n"

    for root, _, files in sorted(os.walk(".")):
        if (
            ".venv" in root
            or "venv" in root
            or "node_modules" in root
            or ".git" in root
            or ".cursor" in root
        ):
            continue
        for file in sorted(files):
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                logging.info(f"Processing {filepath}")
                file_docs = parse_file_for_docs(filepath)
                if (
                    file_docs and "###" in file_docs
                ):  # Only add if there is something documented
                    docs_content += file_docs

    os.makedirs("docs", exist_ok=True)
    with open("docs/api_reference.md", "w", encoding="utf-8") as f:
        f.write(docs_content)
    logging.info("docs/api_reference.md generated successfully.")


if __name__ == "__main__":
    main()
