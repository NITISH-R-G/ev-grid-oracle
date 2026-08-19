import os
import ast
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_python_file(filepath: str) -> dict[str, list[dict[str, str]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            logger.warning(f"Failed to parse {filepath}: {e}")  # noqa: BLE001
            return {"classes": [], "functions": []}

    info: dict[str, list[dict[str, str]]] = {"classes": [], "functions": []}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            info["classes"].append(
                {"name": node.name, "docstring": ast.get_docstring(node) or ""}
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            info["functions"].append(
                {"name": node.name, "docstring": ast.get_docstring(node) or ""}
            )
    return info


def generate_docs():
    docs_dir = "docs"
    os.makedirs(docs_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                info = parse_python_file(filepath)

                if not info["classes"] and not info["functions"]:
                    continue

                rel_path = os.path.relpath(filepath, ".")
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                out_path = os.path.join(docs_dir, safe_name)

                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(f"# Documentation for {rel_path}\n\n")
                    if info["classes"]:
                        f.write("## Classes\n\n")
                        for cls in info["classes"]:
                            f.write(f"### {cls['name']}\n")
                            if cls["docstring"]:
                                f.write(f"```text\n{cls['docstring']}\n```\n\n")

                    if info["functions"]:
                        f.write("## Functions\n\n")
                        for func in info["functions"]:
                            f.write(f"### {func['name']}\n")
                            if func["docstring"]:
                                f.write(f"```text\n{func['docstring']}\n```\n\n")
                logger.info(f"Generated docs for {rel_path} at {out_path}")


if __name__ == "__main__":
    generate_docs()
