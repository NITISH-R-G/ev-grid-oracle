import ast
import os


def generate_docs() -> None:
    os.makedirs("docs/api", exist_ok=True)

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden system directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        # ignore some other obvious non-source directories
        dirs[:] = [
            d for d in dirs if d not in ("node_modules", "artifacts", "web", "docs")
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue  # nosec B112

            try:
                tree = ast.parse(content)
            except SyntaxError:
                continue

            doc_content = f"# API Reference for `{filepath}`\n\n"
            has_content = False

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    has_content = True
                    docstring = ast.get_docstring(node) or "No docstring available."
                    doc_content += f"## Class: `{node.name}`\n\n{docstring}\n\n"
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    has_content = True
                    docstring = ast.get_docstring(node) or "No docstring available."
                    doc_content += f"## Function: `{node.name}`\n\n{docstring}\n\n"

            if has_content:
                # Construct path-safe filenames by incorporating the relative directory path
                safe_name = (
                    filepath.replace("./", "").replace("/", "_").replace(".py", ".md")
                )
                out_path = os.path.join("docs/api", safe_name)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(doc_content)


if __name__ == "__main__":
    generate_docs()
