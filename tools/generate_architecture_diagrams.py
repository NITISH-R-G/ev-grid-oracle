import ast
import os


def generate_architecture_diagram(root_dir="."):
    modules = set()
    dependencies = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        dirnames[:] = [
            d
            for d in dirnames
            if d
            not in ("node_modules", "venv", "dashboard_output", "artifacts", "docs")
        ]

        for file in filenames:
            if file.endswith(".py"):
                filepath = os.path.join(dirpath, file)
                module_name = filepath.replace(".py", "").replace("/", ".")
                modules.add(module_name)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=filepath)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                dependencies.append((module_name, alias.name))
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                dependencies.append((module_name, node.module))
                except Exception:  # nosec B110
                    pass

    diagram = "```mermaid\ngraph TD;\n"
    for mod in modules:
        safe_mod = mod.replace(".", "_")
        diagram += f'    {safe_mod}["{mod}"];\n'

    for src, dst in dependencies:
        safe_src = src.replace(".", "_")
        safe_dst = dst.replace(".", "_")
        diagram += f"    {safe_src} --> {safe_dst};\n"

    diagram += "```\n"

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/architecture_graph.md", "w", encoding="utf-8") as f:
        f.write("# Architecture Diagram\n\n")
        f.write(
            "This diagram is automatically generated based on static code analysis.\n\n"
        )
        f.write(diagram)


if __name__ == "__main__":
    generate_architecture_diagram()
