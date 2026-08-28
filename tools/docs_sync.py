import ast
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_docs(source_dir=".", output_dir="docs"):
    os.makedirs(output_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        if any(
            ignored in root
            for ignored in [".git", ".venv", "__pycache__", "node_modules", ".cursor"]
        ):
            continue

        for file in files:
            if file.endswith(".py") and not file.startswith("test_"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()

                    tree = ast.parse(source_code)

                    classes = []
                    functions = []

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            docstring = ast.get_docstring(node)
                            classes.append({"name": node.name, "docstring": docstring})
                        elif isinstance(node, ast.FunctionDef) and not getattr(
                            node, "is_method", False
                        ):
                            # Basic heuristic, better parsing is possible.
                            docstring = ast.get_docstring(node)
                            functions.append(
                                {"name": node.name, "docstring": docstring}
                            )

                    if classes or functions:
                        # Construct a path-safe filename to prevent collisions.
                        rel_path = os.path.relpath(file_path, source_dir)
                        safe_name = rel_path.replace(os.path.sep, "_").replace(
                            ".py", ".md"
                        )
                        out_path = os.path.join(output_dir, safe_name)

                        with open(out_path, "w", encoding="utf-8") as out:
                            out.write(f"# Documentation for {rel_path}\n\n")
                            if classes:
                                out.write("## Classes\n\n")
                                for c in classes:
                                    out.write(f"### {c['name']}\n")
                                    out.write(
                                        f"{c['docstring'] or 'No docstring provided.'}\n\n"
                                    )
                            if functions:
                                out.write("## Functions\n\n")
                                for f_item in functions:
                                    out.write(f"### {f_item['name']}\n")
                                    out.write(
                                        f"{f_item['docstring'] or 'No docstring provided.'}\n\n"
                                    )

                        logger.info(f"Generated docs for {rel_path} at {out_path}")
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")


if __name__ == "__main__":
    generate_docs()
