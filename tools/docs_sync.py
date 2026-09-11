import ast
import os


def generate_docs(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        if not root.startswith("."):  # ignore hidden
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    path = os.path.join(root, file)
                    rel_path = os.path.relpath(path, src_dir)
                    dest_file = os.path.join(
                        dest_dir,
                        rel_path.replace(os.path.sep, "_").replace(".py", ".md"),
                    )
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        # simple parsing
                        try:
                            tree = ast.parse(content)
                            with open(dest_file, "w", encoding="utf-8") as out:
                                out.write(f"# {rel_path}\n\n")
                                doc = ast.get_docstring(tree)
                                if doc:
                                    out.write(f"{doc}\n\n")
                        except Exception:  # nosec B110  # noqa: BLE001
                            pass


if __name__ == "__main__":
    generate_docs(".", "docs/api/")
