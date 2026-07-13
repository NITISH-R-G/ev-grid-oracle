#!/usr/bin/env python3
"""
Generates a knowledge graph of the repository using AST.
"""

import ast
import json
import os
import networkx as nx


def extract_info_from_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)

        classes = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)

        return {"classes": classes, "functions": functions}
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None


def build_knowledge_graph(repo_root):
    G = nx.DiGraph()

    python_files = []
    for root, _, files in os.walk(repo_root):
        if ".venv" in root or "node_modules" in root or ".git" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    for py_file in python_files:
        rel_path = os.path.relpath(py_file, repo_root)
        G.add_node(rel_path, type="file")

        info = extract_info_from_file(py_file)
        if info:
            for cls in info["classes"]:
                node_name = f"{rel_path}:{cls}"
                G.add_node(node_name, type="class")
                G.add_edge(rel_path, node_name, type="contains")
            for func in info["functions"]:
                node_name = f"{rel_path}:{func}"
                G.add_node(node_name, type="function")
                G.add_edge(rel_path, node_name, type="contains")

    return G


def save_graph(G, output_path):
    data = nx.node_link_data(G)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    G = build_knowledge_graph(repo_root)
    output_path = os.path.join(repo_root, "artifacts", "knowledge_graph.json")
    save_graph(G, output_path)
    print(f"Knowledge graph saved to {output_path}")
