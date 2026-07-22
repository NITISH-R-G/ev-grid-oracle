import ast
import os
import logging
import json
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def sync_docs(repo_path: str = ".") -> None:
    docs_info: Dict[str, Optional[str]] = {}
    for root, _, files in os.walk(repo_path):
        if (
            "node_modules" in root
            or ".venv" in root
            or ".git" in root
            or "build" in root
            or "__pycache__" in root
        ):
            continue
        for file in files:
            if file.endswith(".py"):
                file_path: str = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree: ast.Module = ast.parse(f.read(), filename=file_path)

                    doc: Optional[str] = ast.get_docstring(tree)
                    if doc:
                        docs_info[file_path] = doc
                except Exception as e:
                    logging.warning(f"Failed to process docs for {file_path}: {e}")

    os.makedirs("docs", exist_ok=True)
    try:
        with open("docs/docs_sync_output.json", "w", encoding="utf-8") as f:
            json.dump(docs_info, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to write docs sync output: {e}")


if __name__ == "__main__":
    sync_docs()
