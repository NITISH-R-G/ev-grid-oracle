import ast
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def extract_docstrings(filepath: Path) -> dict[str, Any]:
    """Extract docstrings from classes and functions in a Python file using ast."""
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=str(filepath))
        except SyntaxError as e:
            logger.warning(f"SyntaxError parsing {filepath}: {e}")
            return {"module": "", "classes": [], "functions": []}

    module_doc = ast.get_docstring(tree) or "No module docstring."
    classes: list[dict[str, str]] = []
    functions: list[dict[str, str]] = []

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            classes.append(
                {"name": node.name, "doc": ast.get_docstring(node) or "No docstring."}
            )
            for sub_node in node.body:
                if isinstance(sub_node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": f"{node.name}.{sub_node.name}",
                            "doc": ast.get_docstring(sub_node) or "No docstring.",
                        }
                    )
        elif isinstance(node, ast.FunctionDef):
            functions.append(
                {"name": node.name, "doc": ast.get_docstring(node) or "No docstring."}
            )

    return {"module": module_doc, "classes": classes, "functions": functions}


def generate_markdown(filepath: Path, data: dict[str, Any]) -> str:
    """Generate a simple markdown documentation string from extracted data."""
    md = f"# Documentation for {filepath}\n\n"
    md += f"## Module Docstring\n\n{data['module']}\n\n"

    if data["classes"]:
        md += "## Classes\n\n"
        for c in data["classes"]:
            md += f"### {c['name']}\n{c['doc']}\n\n"

    if data["functions"]:
        md += "## Functions\n\n"
        for f in data["functions"]:
            md += f"### {f['name']}\n{f['doc']}\n\n"

    return md


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting documentation synchronization...")

    root_dir = Path(".")
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Also ignore some common build/virtualenv dirs if they are not hidden
        dirnames[:] = [
            d
            for d in dirnames
            if d not in ("venv", "build", "dist", "node_modules", "dashboard_output")
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = Path(dirpath) / filename
                rel_path = filepath.relative_to(root_dir)

                # Construct path-safe filenames by incorporating the relative directory path
                safe_name = str(rel_path).replace(os.sep, "_").replace(".py", ".md")
                out_path = docs_dir / safe_name

                data = extract_docstrings(filepath)
                if (
                    data["classes"]
                    or data["functions"]
                    or data["module"] != "No module docstring."
                ):
                    md_content = generate_markdown(filepath, data)
                    with open(out_path, "w", encoding="utf-8") as out_f:
                        out_f.write(md_content)
                    logger.info(f"Generated docs for {filepath} -> {out_path}")

    logger.info("Documentation synchronization complete.")


if __name__ == "__main__":
    main()
