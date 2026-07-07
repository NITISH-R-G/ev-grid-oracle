import ast
import json
from pathlib import Path
from typing import Dict, Any, List


from typing import Tuple


def parse_python_file(
    filepath: Path, repo_root: Path
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Parses a Python file and extracts classes, functions, and relationships."""
    rel_path = str(filepath.relative_to(repo_root))
    file_node = {"id": rel_path, "type": "file", "name": filepath.name}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
    except Exception:
        return [file_node], []

    nodes = [file_node]
    edges = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_id = f"{rel_path}:{node.name}"
            nodes.append({"id": class_id, "type": "class", "name": node.name})
            edges.append({"source": rel_path, "target": class_id, "type": "contains"})
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    func_id = f"{class_id}.{item.name}"
                    nodes.append({"id": func_id, "type": "function", "name": item.name})
                    edges.append(
                        {"source": class_id, "target": func_id, "type": "contains"}
                    )
        elif isinstance(node, ast.FunctionDef):
            func_id = f"{rel_path}:{node.name}"
            nodes.append({"id": func_id, "type": "function", "name": node.name})
            edges.append({"source": rel_path, "target": func_id, "type": "contains"})

    return nodes, edges


def generate_graph():
    """Generates a comprehensive knowledge graph by analyzing Python source files."""
    repo_root = Path(__file__).parent.parent

    all_nodes: List[Dict[str, Any]] = []
    all_edges: List[Dict[str, str]] = []

    # Process Python files
    for py_file in repo_root.rglob("*.py"):
        if any(
            part in (".venv", "venv", "node_modules", ".git", ".pytest_cache")
            for part in py_file.parts
        ):
            continue

        nodes, edges = parse_python_file(py_file, repo_root)
        all_nodes.extend(nodes)
        all_edges.extend(edges)

    # Create the graph
    graph = {"nodes": all_nodes, "edges": all_edges}

    output_file = repo_root / "knowledge_graph.json"
    with open(output_file, "w") as f:
        json.dump(graph, f, indent=2)

    print(
        f"Generated knowledge graph with {len(all_nodes)} nodes and {len(all_edges)} edges."
    )


if __name__ == "__main__":
    generate_graph()
