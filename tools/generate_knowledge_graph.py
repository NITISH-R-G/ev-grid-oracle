import ast
import json
import os
from typing import Any, Dict, List


def extract_info(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
        except Exception:
            return []

    info = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            info.append({"type": "class", "name": node.name})
            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    info.append(
                        {
                            "type": "method",
                            "name": subnode.name,
                            "parent": node.name,
                        }
                    )
        elif isinstance(node, ast.FunctionDef):
            info.append({"type": "function", "name": node.name})
    return info


def generate_knowledge_graph(src_dirs: List[str], out_file: str) -> None:
    graph: Dict[str, List[Dict[str, Any]]] = {}
    for src_dir in src_dirs:
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    info = extract_info(filepath)
                    if info:
                        graph[filepath] = info

    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph(["ev_grid_oracle", "server"], "docs/knowledge_graph.json")
