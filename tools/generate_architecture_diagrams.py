import ast
import os
import pathlib


def find_imports(filepath: str) -> list[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
        tree = ast.parse(code)
    except Exception:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    return imports


def generate_mermaid():
    root = pathlib.Path(".")
    out_dir = pathlib.Path("artifacts")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "architecture_graph.md"

    mermaid_lines = ["```mermaid", "graph TD"]

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        if "node_modules" in dirpath or "dist" in dirpath or "venv" in dirpath:
            continue

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                imports = find_imports(filepath)

                module_name = filepath.replace("/", ".").replace(".py", "")
                # simplified module name for nodes
                module_name = module_name.lstrip(".")

                for imp in imports:
                    mermaid_lines.append(f"    {module_name} --> {imp}")

    mermaid_lines.append("```\n")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Graph\n\n")
        f.write("\n".join(mermaid_lines))


if __name__ == "__main__":
    generate_mermaid()
    print("Architecture diagram generated.")
