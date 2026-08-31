import ast
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def sync_docs() -> None:
    docs_dir = Path("docs/api")
    docs_dir.mkdir(parents=True, exist_ok=True)

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        # Also ignore some standard build/artifact directories
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                "node_modules",
                "artifacts",
                "build",
                "dist",
                "dashboard_output",
                "docs",
                "web",
            )
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Construct path-safe filename by replacing os.sep with "_"
                rel_path = os.path.relpath(filepath, ".")
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                out_path = docs_dir / safe_name

                with open(out_path, "w", encoding="utf-8") as out:
                    out.write(f"# Documentation for `{rel_path}`\n\n")

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        out.write(f"## Module Docstring\n\n{module_doc}\n\n")

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            out.write(f"## Class: `{node.name}`\n\n")
                            cls_doc = ast.get_docstring(node)
                            if cls_doc:
                                out.write(f"{cls_doc}\n\n")
                        elif isinstance(node, ast.FunctionDef) or isinstance(
                            node, ast.AsyncFunctionDef
                        ):
                            out.write(f"## Function: `{node.name}`\n\n")
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                out.write(f"{func_doc}\n\n")

            except SyntaxError as e:
                logger.warning("SyntaxError parsing %s: %s", filepath, e)
            except OSError as e:
                logger.warning("OSError reading %s: %s", filepath, e)


if __name__ == "__main__":
    sync_docs()
