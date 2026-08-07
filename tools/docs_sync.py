import ast
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def sync_docs() -> None:
    docs: dict[str, list[dict[str, Any]]] = {}
    for root, dirs, files in os.walk("."):
        if not root.startswith("."):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    docs[path] = []
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            tree = ast.parse(f.read(), filename=path)
                            for node in ast.walk(tree):
                                if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                                    docstring = ast.get_docstring(node)
                                    if docstring:
                                        docs[path].append(
                                            {"name": node.name, "doc": docstring}
                                        )
                    except Exception as e:
                        logger.warning("Error parsing %s: %s", path, e)

    with open("docs_sync.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)


if __name__ == "__main__":
    sync_docs()
