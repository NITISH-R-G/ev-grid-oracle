import ast
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOCS_DIR = "docs"


def parse_python_file(filepath: str) -> dict:
    """Parses a Python file and extracts its structure using ast."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        logger.warning(f"Failed to parse {filepath}: {e}")
        return {}

    classes = []
    functions = []

    module_docstring = ast.get_docstring(tree)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node)
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            classes.append(
                {"name": node.name, "docstring": class_doc, "methods": methods}
            )
        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node)
            functions.append({"name": node.name, "docstring": func_doc})

    return {
        "module_docstring": module_docstring,
        "classes": classes,
        "functions": functions,
    }


def generate_markdown(filepath: str, structure: dict) -> str:
    """Generates a Markdown documentation string for a Python file's structure."""
    md = f"# Documentation for `{filepath}`\n\n"

    if structure.get("module_docstring"):
        md += f"## Module Overview\n{structure['module_docstring']}\n\n"

    if structure.get("classes"):
        md += "## Classes\n\n"
        for cls in structure["classes"]:
            md += f"### {cls['name']}\n"
            if cls["docstring"]:
                md += f"{cls['docstring']}\n"
            if cls["methods"]:
                md += "\n**Methods:**\n"
                for method in cls["methods"]:
                    md += f"- `{method}`\n"
            md += "\n"

    if structure.get("functions"):
        md += "## Functions\n\n"
        for func in structure["functions"]:
            md += f"### {func['name']}\n"
            if func["docstring"]:
                md += f"{func['docstring']}\n"
            md += "\n"

    return md


def sync_docs():
    """Main function to parse all Python files and generate Markdown documentation."""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)

    for root, _, files in os.walk("."):
        # Ignore hidden system directories like .git, .github, .venv
        if os.path.basename(root).startswith(".") or any(
            part.startswith(".") and part != "." for part in root.split(os.sep)
        ):
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                # Skip files inside tests or tools, modify as needed
                if "tests" in filepath or "tools" in filepath:
                    continue

                structure = parse_python_file(filepath)
                if not structure or (
                    not structure.get("classes") and not structure.get("functions")
                ):
                    continue

                md_content = generate_markdown(filepath, structure)

                # Construct safe output filename using relative path to prevent collisions
                safe_name = (
                    filepath.replace("./", "").replace("/", "_").replace(".py", ".md")
                )
                out_path = os.path.join(DOCS_DIR, safe_name)

                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(md_content)
                logger.info(f"Generated docs for {filepath} -> {out_path}")


if __name__ == "__main__":
    sync_docs()
