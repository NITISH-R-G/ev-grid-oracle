import ast
import logging
import os

logging.basicConfig(level=logging.INFO)


def extract_docstrings(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        docs = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                if docstring:
                    name = getattr(node, "name", "Module")
                    docs.append(f"### {name}\n\n{docstring}\n")
        return docs
    except Exception as e:
        logging.warning(f"Failed to parse {filepath}: {e}")
        return []


def generate_docs(root_dir="."):
    os.makedirs("docs/api", exist_ok=True)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if any(
            d in dirpath
            for d in [
                ".git",
                "__pycache__",
                ".venv",
                "node_modules",
                "venv",
                "artifacts",
                "docs",
            ]
        ):
            continue
        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                docs = extract_docstrings(filepath)
                if docs:
                    safe_name = (
                        os.path.relpath(filepath, root_dir)
                        .replace(os.sep, "_")
                        .replace(".py", ".md")
                    )
                    out_path = os.path.join("docs/api", safe_name)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(f"# Documentation for {filepath}\n\n")
                        f.write("\n".join(docs))
                    logging.info(f"Generated doc for {filepath} at {out_path}")


if __name__ == "__main__":
    generate_docs()
