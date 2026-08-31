import ast
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def generate_architecture_diagrams() -> None:
    architecture: dict[str, list[str]] = {}

    for root, dirs, files in os.walk("."):
        # Explicitly ignore hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        # Also ignore some standard build/artifact directories
        dirs[:] = [
            d
            for d in dirs
            if d
            not in (
                "node_modules",
                "artifacts",
                "build",
                "dist",
                "dashboard_output",
                "docs",
                "web",
            )
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, ".")
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)
                imports: list[str] = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module)

                # Make it deterministic
                architecture[rel_path] = sorted(list(set(imports)))

            except SyntaxError as e:
                logger.warning("SyntaxError parsing %s: %s", filepath, e)
            except OSError as e:
                logger.warning("OSError reading %s: %s", filepath, e)

    output_dir = Path("artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "architecture_graph.json", "w", encoding="utf-8") as f:
        json.dump(architecture, f, indent=2)


if __name__ == "__main__":
    generate_architecture_diagrams()
