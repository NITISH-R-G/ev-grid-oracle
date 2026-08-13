import ast
import json
import os


def extract_info(filepath: str) -> dict[str, list[dict[str, str | None]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except SyntaxError:
            return {"classes": [], "functions": []}

    classes: list[dict[str, str | None]] = []
    functions: list[dict[str, str | None]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            docstring = ast.get_docstring(node)
            classes.append(
                {
                    "name": node.name,
                    "docstring": docstring,
                }
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            # Only record top-level or method-level functions if needed,
            # here we just grab all function defs
            docstring = ast.get_docstring(node)
            functions.append(
                {
                    "name": node.name,
                    "docstring": docstring,
                }
            )

    return {"classes": classes, "functions": functions}


def generate_knowledge_graph(
    root_dir: str = ".",
) -> dict[str, dict[str, list[dict[str, str | None]]]]:
    graph: dict[str, dict[str, list[dict[str, str | None]]]] = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden system directories
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                info = extract_info(filepath)
                if info["classes"] or info["functions"]:
                    graph[rel_path] = info
    return graph


if __name__ == "__main__":
    graph = generate_knowledge_graph()
    output_path = os.path.join("docs", "knowledge_graph.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    print(f"Knowledge graph generated at {output_path}")
