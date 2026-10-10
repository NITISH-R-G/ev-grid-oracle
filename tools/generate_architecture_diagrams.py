import ast
import os
from pathlib import Path


def generate_diagrams() -> None:
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    root_dir = Path(".")

    modules = set()
    imports = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories (e.g. .git, .github, .venv)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        # Ignore common build/test directories
        if any(
            ignored in dirpath
            for ignored in [
                "node_modules",
                "__pycache__",
                "dist",
                "build",
                "artifacts",
                "docs",
            ]
        ):
            continue

        for file in filenames:
            if file.endswith(".py"):
                file_path = Path(dirpath) / file
                module_name = (
                    str(file_path)
                    .replace("/", ".")
                    .replace("\\", ".")
                    .replace(".py", "")
                )
                modules.add(module_name)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)

                    for node in tree.body:
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append((module_name, alias.name))
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.append((module_name, node.module))
                except Exception as e:  # noqa: BLE001
                    print(f"Failed to parse {file_path}: {e}")

    # Generate Mermaid diagram
    mermaid = "```mermaid\ngraph TD;\n"

    for mod in modules:
        mermaid += f'    {mod.replace(".", "_")} ["{mod}"];\n'

    for source, target in imports:
        # Filter for local imports mostly, simple heuristic
        if any(target.startswith(m.split(".")[0]) for m in modules):
            mermaid += (
                f"    {source.replace('.', '_')} --> {target.replace('.', '_')};\n"
            )

    mermaid += "```\n"

    out_path = artifacts_dir / "architecture_graph.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Architecture Diagram\n\n")
        f.write(mermaid)


if __name__ == "__main__":
    generate_diagrams()
