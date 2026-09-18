import ast
import os


def main() -> None:
    print("Starting docs_sync.py...")

    root_dir = "."
    out_dir = os.path.join("docs", "api")
    os.makedirs(out_dir, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames[:] = [
            d
            for d in dirnames
            if d not in ("node_modules", "venv", "__pycache__", "artifacts")
        ]

        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            filepath = os.path.join(dirpath, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                try:
                    tree = ast.parse(content, filename=filepath)

                    docstrings: list[str] = []
                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        docstrings.append(f"# Module: {filepath}\n\n{module_doc}\n")

                    for node in ast.walk(tree):
                        if isinstance(
                            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                        ):
                            doc = ast.get_docstring(node)
                            if doc:
                                kind = (
                                    "Class"
                                    if isinstance(node, ast.ClassDef)
                                    else "Function"
                                )
                                docstrings.append(f"## {kind}: {node.name}\n\n{doc}\n")

                    if docstrings:
                        # Path-safe filename
                        safe_name = filepath.replace("/", "_").replace("\\", "_")
                        safe_name = safe_name.removeprefix("._")
                        out_file = os.path.join(
                            out_dir, safe_name.replace(".py", ".md")
                        )
                        with open(out_file, "w", encoding="utf-8") as f:
                            f.write("\n".join(docstrings))

                except SyntaxError:
                    pass
                except Exception:  # nosec B110 # noqa: BLE001
                    pass
            except Exception:  # nosec B110 # noqa: BLE001
                pass

    print(f"API docs synced to {out_dir}")


if __name__ == "__main__":
    main()
