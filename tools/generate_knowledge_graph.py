import os
import ast
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_info_from_file(filepath):
    """Parses a Python file and extracts functions, classes, and their docstrings."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content)
    except Exception as e:
        logging.warning(f"Failed to parse {filepath}: {e}")
        return None

    from typing import Dict, List, Any

    info: Dict[str, List[Dict[str, Any]]] = {"classes": [], "functions": []}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            info["classes"].append(
                {"name": node.name, "docstring": ast.get_docstring(node)}
            )
        elif isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        ):
            info["functions"].append(
                {"name": node.name, "docstring": ast.get_docstring(node)}
            )

    return info if (info["classes"] or info["functions"]) else None


def generate_knowledge_graph(root_dir, skip_dirs=None):
    """Generates a knowledge graph of the repository."""
    if skip_dirs is None:
        skip_dirs = {
            ".git",
            ".github",
            "__pycache__",
            ".venv",
            "venv",
            "node_modules",
            "dist",
            "build",
            ".mypy_cache",
            ".pytest_cache",
        }

    knowledge_graph = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modify dirnames in-place to skip specific directories
        dirnames[:] = [
            d for d in dirnames if d not in skip_dirs and not d.startswith(".")
        ]

        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)
                file_info = extract_info_from_file(filepath)
                if file_info:
                    knowledge_graph[rel_path] = file_info

    return knowledge_graph


def save_knowledge_graph(graph, json_path, md_path):
    """Saves the knowledge graph to JSON and Markdown formats."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(json_path), exist_ok=True)

    # Save as JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=4)

    # Save as Markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Repository Knowledge Graph\n\n")
        f.write(
            "This document provides a high-level overview of the classes and functions within the repository.\n\n"
        )

        for filepath, info in sorted(graph.items()):
            f.write(f"## `{filepath}`\n\n")

            if info["classes"]:
                f.write("### Classes\n")
                for cls in info["classes"]:
                    f.write(f"- **`{cls['name']}`**\n")
                    if cls["docstring"]:
                        f.write(f"  - {cls['docstring'].splitlines()[0]}\n")

            if info["functions"]:
                f.write("### Functions\n")
                for func in info["functions"]:
                    f.write(f"- **`{func['name']}`**\n")
                    if func["docstring"]:
                        f.write(f"  - {func['docstring'].splitlines()[0]}\n")
            f.write("\n")


if __name__ == "__main__":
    root_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    docs_dir = os.path.join(root_directory, "docs")

    json_output_path = os.path.join(docs_dir, "knowledge_graph.json")
    md_output_path = os.path.join(docs_dir, "knowledge_graph.md")

    logging.info(f"Generating knowledge graph for {root_directory}...")
    kg = generate_knowledge_graph(root_directory)

    logging.info(
        f"Saving knowledge graph to {json_output_path} and {md_output_path}..."
    )
    save_knowledge_graph(kg, json_output_path, md_output_path)
    logging.info("Knowledge graph generation complete.")
