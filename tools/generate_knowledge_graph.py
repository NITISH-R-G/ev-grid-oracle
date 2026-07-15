import ast
import json
from pathlib import Path
from typing import Dict, Any


def parse_file(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except Exception as e:
        return {"error": str(e)}

    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "line": node.lineno,
                }
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            functions.append(
                {
                    "name": node.name,
                    "docstring": ast.get_docstring(node),
                    "line": node.lineno,
                }
            )

    return {
        "module_docstring": ast.get_docstring(tree),
        "classes": classes,
        "functions": functions,
    }


def main():
    root_dir = Path(__file__).parent.parent
    graph: Dict[str, Any] = {}

    for py_file in root_dir.rglob("*.py"):
        if (
            ".venv" in py_file.parts
            or "venv" in py_file.parts
            or ".cursor" in py_file.parts
            or "tests" in py_file.parts
        ):
            continue

        rel_path = py_file.relative_to(root_dir)
        graph[str(rel_path)] = parse_file(str(py_file))

    output_path = root_dir / "knowledge_graph.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"Generated knowledge graph at {output_path}")


if __name__ == "__main__":
    main()
