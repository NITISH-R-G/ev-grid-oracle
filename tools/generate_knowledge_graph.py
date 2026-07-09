import os
import ast


def generate_knowledge_graph():
    graph_content = "# Repository Knowledge Graph\n\n"

    for root, _, files in os.walk("."):
        if ".venv" in root or ".git" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        source = f.read()

                    tree = ast.parse(source)
                    classes = [
                        node.name
                        for node in ast.walk(tree)
                        if isinstance(node, ast.ClassDef)
                    ]
                    functions = [
                        node.name
                        for node in ast.walk(tree)
                        if isinstance(node, ast.FunctionDef)
                    ]

                    if classes or functions:
                        graph_content += f"## {filepath}\n"
                        if classes:
                            graph_content += (
                                "- **Classes**: " + ", ".join(classes) + "\n"
                            )
                        if functions:
                            graph_content += (
                                "- **Functions**: " + ", ".join(functions) + "\n"
                            )
                        graph_content += "\n"
                except Exception as e:
                    print(f"Failed to parse {filepath}: {e}")

    with open("KNOWLEDGE_GRAPH.md", "w", encoding="utf-8") as f:
        f.write(graph_content)


if __name__ == "__main__":
    generate_knowledge_graph()
