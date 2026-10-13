import ast
import os
from collections import defaultdict


def extract_imports(filepath: str) -> list[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module.split(".")[0])
    return imports


def generate_mermaid_diagram(dependencies: dict[str, set[str]]) -> str:
    lines = ["```mermaid", "graph TD"]
    for module, deps in dependencies.items():
        if deps:
            for dep in deps:
                # To keep graph readable, we only map internal dependencies (e.g. ones that match top-level folders)
                if dep in [
                    "ev_grid_oracle",
                    "server",
                    "tools",
                    "tests",
                    "training",
                    "viz",
                ]:
                    lines.append(f"    {module} --> {dep}")
        else:
            lines.append(f"    {module}")

    lines.append("```")
    return "\n".join(lines)


def main() -> None:
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(repo_root, "artifacts", "architecture_graph.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    dependencies: dict[str, set[str]] = defaultdict(set)

    for root, dnames, fnames in os.walk(repo_root):
        dnames[:] = [d for d in dnames if not d.startswith(".")]
        if any(
            ignored in root
            for ignored in ["venv", "node_modules", "web/dist", "artifacts"]
        ):
            continue

        # Get top-level module name for the current directory
        rel_path = os.path.relpath(root, repo_root)
        module_name = rel_path.split(os.sep)[0] if rel_path != "." else "root"

        # Ignore external or irrelevant folders from diagram nodes
        if module_name not in [
            "ev_grid_oracle",
            "server",
            "tools",
            "tests",
            "training",
            "viz",
            "root",
        ]:
            continue

        for fname in fnames:
            if fname.endswith(".py"):
                filepath = os.path.join(root, fname)
                imports = extract_imports(filepath)
                dependencies[module_name].update(imports)

    mermaid_code = generate_mermaid_diagram(dependencies)

    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write("# Interactive Architecture Diagram\n\n")
        out_f.write(mermaid_code)
        out_f.write("\n")

    print(f"Architecture diagram generated at {output_path}")


if __name__ == "__main__":
    main()
