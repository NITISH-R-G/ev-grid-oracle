import ast
import json
import os
from typing import Any


def parse_file(filepath: str) -> dict[str, list[dict[str, Any]]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            content = f.read()
            tree = ast.parse(content)
        except Exception: # noqa: BLE001
            # Ignore parse errors for knowledge graph
            return {"classes": [], "functions": []}

    classes: list[dict[str, Any]] = []
    functions: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                "name": node.name,
                "line": node.lineno,
                "type": "class",
                "filepath": filepath
            })
        elif isinstance(node, ast.FunctionDef):
            functions.append({
                "name": node.name,
                "line": node.lineno,
                "type": "function",
                "filepath": filepath
            })

    return {"classes": classes, "functions": functions}

def main() -> None:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for root, dirs, files in os.walk("."):
        if ".git" in root or ".venv" in root or "node_modules" in root or "artifacts" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                result = parse_file(filepath)
                nodes.extend(result["classes"])
                nodes.extend(result["functions"])

                # Add basic edges (file -> class/function)
                file_node_id = filepath
                if not any(n.get("id") == file_node_id for n in nodes):
                     nodes.append({"id": file_node_id, "type": "file", "name": file})

                for cls in result["classes"]:
                    edges.append({"source": file_node_id, "target": cls["name"], "type": "contains"})
                for func in result["functions"]:
                    edges.append({"source": file_node_id, "target": func["name"], "type": "contains"})

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

if __name__ == "__main__":
    main()
