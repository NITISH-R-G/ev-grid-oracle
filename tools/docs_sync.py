import ast
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_docs(filepath: str) -> str:
    docs = f"# Documentation for {filepath}\n\n"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        module_doc = ast.get_docstring(tree)
        if module_doc:
            docs += f"{module_doc}\n\n"
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docs += f"## Class: {node.name}\n"
                class_doc = ast.get_docstring(node)
                if class_doc:
                    docs += f"{class_doc}\n\n"
                else:
                    docs += "No docstring available.\n\n"
            elif isinstance(node, ast.FunctionDef):
                docs += f"### Function: {node.name}\n"
                func_doc = ast.get_docstring(node)
                if func_doc:
                    docs += f"{func_doc}\n\n"
                else:
                    docs += "No docstring available.\n\n"
    except Exception as e:  # noqa: BLE001
        logger.warning(f"Failed to parse {filepath}: {e}")
        docs += f"Error parsing file: {e}\n\n"
    return docs


def sync_docs(root_dir: str, docs_dir: str) -> None:
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if (
                file.endswith(".py")
                and file != "docs_sync.py"
                and file != "generate_knowledge_graph.py"
            ):
                filepath = os.path.join(root, file)
                docs = extract_docs(filepath)
                # Create a flattened filename for docs
                rel_path = os.path.relpath(filepath, root_dir)
                out_filename = rel_path.replace(os.path.sep, "_") + ".md"
                out_filepath = os.path.join(docs_dir, out_filename)
                try:
                    with open(out_filepath, "w", encoding="utf-8") as f:
                        f.write(docs)
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to write docs for {filepath}: {e}")


def main() -> None:
    logger.info("Starting documentation synchronization...")
    sync_docs(".", "docs/api")
    logger.info("Documentation synchronization complete.")


if __name__ == "__main__":
    main()
