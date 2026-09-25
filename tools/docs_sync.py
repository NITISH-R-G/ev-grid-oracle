import ast
import logging
import os

logger = logging.getLogger(__name__)


def generate_docs() -> None:
    out_dir = os.path.join("docs", "api")
    os.makedirs(out_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if "build" in dirs:
            dirs.remove("build")
        if "dist" in dirs:
            dirs.remove("dist")

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Failed to parse {filepath}: {e}")
                continue

            docstring = ast.get_docstring(tree)

            classes_docs: list[str] = []
            functions_docs: list[str] = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    cls_doc = ast.get_docstring(node)
                    if cls_doc:
                        classes_docs.append(f"### Class `{node.name}`\n{cls_doc}\n")
                elif isinstance(node, ast.FunctionDef):
                    fn_doc = ast.get_docstring(node)
                    if fn_doc:
                        functions_docs.append(f"### Function `{node.name}`\n{fn_doc}\n")

            if docstring or classes_docs or functions_docs:
                # Create a path-safe filename based on relative path
                rel_path = os.path.relpath(filepath, ".")
                safe_name = rel_path.replace(os.sep, "_").replace(".py", ".md")
                out_path = os.path.join(out_dir, safe_name)

                with open(out_path, "w", encoding="utf-8") as out:
                    out.write(f"# {rel_path}\n\n")
                    if docstring:
                        out.write(f"## Module Docstring\n{docstring}\n\n")
                    if classes_docs:
                        out.write("## Classes\n")
                        out.writelines(classes_docs)
                    if functions_docs:
                        out.write("## Functions\n")
                        out.writelines(functions_docs)

                logger.info(f"Generated docs for {filepath} at {out_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_docs()
