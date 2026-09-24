import ast
import json
import os
from pathlib import Path


def generate_knowledge_graph(root_dir: str = "."):
    graph: dict[str, list[dict[str, str]]] = {"nodes": []}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Ignore hidden directories (e.g., .git, .venv, .github)
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()

                    module = ast.parse(content)

                    for node in ast.walk(module):
                        if isinstance(node, ast.ClassDef):
                            graph["nodes"].append(
                                {"type": "class", "name": node.name, "file": filepath}
                            )
                        elif isinstance(node, ast.FunctionDef):
                            graph["nodes"].append(
                                {
                                    "type": "function",
                                    "name": node.name,
                                    "file": filepath,
                                }
                            )
                except Exception:  # nosec B110
                    pass  # Ignore files that cannot be parsed

    # Write the graph to artifacts directory
    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)


if __name__ == "__main__":
    generate_knowledge_graph()
