import ast
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def extract_info_from_ast(filepath: str) -> dict[str, list[dict[str, Any]]]:
    info: dict[str, list[dict[str, Any]]] = {"classes": [], "functions": []}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        logger.warning(f"Could not read file {filepath}: {e}")
        return info

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        logger.warning(f"Syntax error in {filepath}: {e}")
        return info

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info: dict[str, Any] = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
            }
            info["classes"].append(class_info)
        elif isinstance(node, ast.FunctionDef):
            func_info: dict[str, Any] = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
            }
            info["functions"].append(func_info)

    return info


def generate_markdown(filepath: str, info: dict[str, list[dict[str, Any]]]) -> str:
    md_content = f"# Documentation for `{filepath}`\n\n"

    if info["classes"]:
        md_content += "## Classes\n\n"
        for cls in info["classes"]:
            md_content += f"### `{cls['name']}`\n"
            if cls["docstring"]:
                md_content += f"{cls['docstring']}\n\n"
            else:
                md_content += "*No docstring available.*\n\n"

    if info["functions"]:
        md_content += "## Functions\n\n"
        for func in info["functions"]:
            md_content += f"### `{func['name']}`\n"
            if func["docstring"]:
                md_content += f"{func['docstring']}\n\n"
            else:
                md_content += "*No docstring available.*\n\n"

    return md_content


def sync_docs(root_dir: str = ".") -> None:
    docs_dir = "docs/api"
    os.makedirs(docs_dir, exist_ok=True)

    skip_dirs = {
        ".git",
        ".github",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "node_modules",
        "build",
        "dist",
        "artifacts",
        ".cursor",
        "docs",
        ".mypy_cache",
        ".pytest_cache",
    }

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                info = extract_info_from_ast(filepath)
                if info["classes"] or info["functions"]:
                    md_content = generate_markdown(filepath, info)

                    # Create a safe filename for the doc
                    doc_filename = filepath.replace(os.path.sep, "_").replace(
                        ".py", ".md"
                    )
                    doc_filename = doc_filename.removeprefix("._")

                    doc_path = os.path.join(docs_dir, doc_filename)
                    with open(doc_path, "w", encoding="utf-8") as f:
                        f.write(md_content)

                    logger.info(f"Generated docs for {filepath} at {doc_path}")


def main() -> None:
    logger.info("Starting documentation sync...")
    sync_docs()
    logger.info("Documentation sync complete.")


if __name__ == "__main__":
    main()
