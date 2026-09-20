import ast
import logging
import os
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sanitize_filename(filepath: str) -> str:
    """Creates a path-safe filename based on the relative path to prevent collisions."""
    filepath = filepath.removeprefix("./")
    safe_name = re.sub(r"[^a-zA-Z0-9]", "_", filepath)
    safe_name = safe_name.removesuffix("_py")
    return safe_name + ".md"


def sync_docs() -> None:
    docs_dir = os.path.join("docs", "api")
    os.makedirs(docs_dir, exist_ok=True)

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d
            not in (
                "node_modules",
                "dist",
                "artifacts",
                "web",
                "assets",
                "dashboard_output",
                "docs",
                "ev_oracle_grpo_road",
                "ev_oracle_lora",
                "ev_oracle_merged_16bit",
                "ev_grid_oracle.egg-info",
                "build",
            )
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()

                    module = ast.parse(source)

                    doc_content = f"# Module: `{file_path}`\n\n"
                    doc_content += f"**Description:**\n{ast.get_docstring(module) or '*No module docstring provided.*'}\n\n"

                    for item in module.body:
                        if isinstance(item, ast.FunctionDef):
                            doc_content += f"## Function: `{item.name}`\n"
                            doc_content += f"{ast.get_docstring(item) or '*No function docstring provided.*'}\n\n"
                        elif isinstance(item, ast.ClassDef):
                            doc_content += f"## Class: `{item.name}`\n"
                            doc_content += f"{ast.get_docstring(item) or '*No class docstring provided.*'}\n\n"

                            for class_item in item.body:
                                if isinstance(class_item, ast.FunctionDef):
                                    doc_content += (
                                        f"### Method: `{item.name}.{class_item.name}`\n"
                                    )
                                    doc_content += f"{ast.get_docstring(class_item) or '*No method docstring provided.*'}\n\n"

                    out_name = sanitize_filename(file_path)
                    out_path = os.path.join(docs_dir, out_name)

                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(doc_content)
                except Exception as e:  # noqa: BLE001
                    logger.warning(f"Failed to process docs for {file_path}: {e}")


if __name__ == "__main__":
    sync_docs()
    logger.info("Documentation sync complete.")
