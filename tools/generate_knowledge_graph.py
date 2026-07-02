import os
import json
from typing import Dict, List

def generate_knowledge_graph() -> None:
    print("Generating knowledge graph...")
    graph: Dict[str, List[Dict[str, str]]] = {"nodes": [], "edges": []}
    for root, dirs, files in os.walk("."):
        if ".git" in root or "node_modules" in root or ".venv" in root:
            continue
        for file in files:
            if file.endswith((".py", ".ts", ".md", ".json", ".yml", ".yaml")):
                filepath = os.path.join(root, file)
                graph["nodes"].append({"id": filepath, "label": file})

    os.makedirs("artifacts", exist_ok=True)
    with open("artifacts/knowledge_graph.json", "w") as f:
        json.dump(graph, f, indent=2)

if __name__ == "__main__":
    generate_knowledge_graph()
