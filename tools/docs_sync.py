import ast
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def sync_docs(root_dir="."):
    os.makedirs("docs/api", exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        if 'node_modules' in dirnames:
            dirnames.remove('node_modules')

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                rel_path = os.path.relpath(filepath, root_dir)

                classes = []
                functions = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        doc = ast.get_docstring(node) or "No documentation provided."
                        classes.append(f"### Class `{node.name}`\n\n{doc}\n")
                    elif isinstance(node, ast.FunctionDef):
                        # skip top-level functions in tests for brevity if needed
                        doc = ast.get_docstring(node) or "No documentation provided."
                        functions.append(f"### Function `{node.name}`\n\n{doc}\n")

                if classes or functions:
                    safe_name = rel_path.replace(os.sep, '_').replace('.py', '.md')
                    out_path = os.path.join("docs/api", safe_name)

                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Documentation for `{rel_path}`\n\n")
                        if classes:
                            f.write("## Classes\n\n")
                            f.write("\n".join(classes))
                        if functions:
                            f.write("\n## Functions\n\n")
                            f.write("\n".join(functions))

            except Exception as e:  # noqa: BLE001  # noqa: BLE001  # noqa: BLE001
                logger.warning(f"Failed to process docs for {filepath}: {e}")

    logger.info("API documentation generated in docs/api/")

if __name__ == "__main__":
    sync_docs()
