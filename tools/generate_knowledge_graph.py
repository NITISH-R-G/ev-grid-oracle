import ast
import json
import os
from typing import Dict, List, Any


def generate_knowledge_graph(root_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    info: Dict[str, List[Dict[str, Any]]] = {"files": []}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip common non-source directories
        if any(
            d in dirpath
            for d in [
                ".git",
                "node_modules",
                ".venv",
                "venv",
                "__pycache__",
                ".github",
                "docs",
                "assets",
            ]
        ):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()
                    parsed = ast.parse(source)
                    file_info: Dict[str, Any] = {
                        "path": filepath,
                        "classes": [],
                        "functions": [],
                    }
                    for node in ast.walk(parsed):
                        if isinstance(node, ast.ClassDef):
                            file_info["classes"].append(node.name)
                        elif isinstance(node, ast.FunctionDef):
                            file_info["functions"].append(node.name)
                    info["files"].append(file_info)
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")
    return info


if __name__ == "__main__":
    kg = generate_knowledge_graph(".")
    os.makedirs("docs", exist_ok=True)
    with open("docs/knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(kg, f, indent=2)
    print("Knowledge graph generated at docs/knowledge_graph.json")
