import os
import ast
from typing import Any

def generate_docs(root_dir: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(dirpath, filename)
            rel_dir = os.path.relpath(dirpath, root_dir)
            if rel_dir == '.':
                rel_dir = ''

            base_name = os.path.splitext(filename)[0]
            if rel_dir:
                safe_name = f"{rel_dir.replace(os.sep, '_')}_{base_name}.md"
            else:
                safe_name = f"{base_name}.md"

            out_path = os.path.join(output_dir, safe_name)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                module = ast.parse(content)
                doc_lines: list[str] = [f"# {base_name}", ""]

                module_doc = ast.get_docstring(module)
                if module_doc:
                    doc_lines.extend([module_doc, ""])

                for node in module.body:
                    if isinstance(node, ast.ClassDef):
                        doc_lines.extend([f"## Class: `{node.name}`", ""])
                        class_doc = ast.get_docstring(node)
                        if class_doc:
                            doc_lines.extend([class_doc, ""])

                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                doc_lines.extend([f"### Method: `{item.name}`", ""])
                                method_doc = ast.get_docstring(item)
                                if method_doc:
                                    doc_lines.extend([method_doc, ""])

                    elif isinstance(node, ast.FunctionDef):
                        doc_lines.extend([f"## Function: `{node.name}`", ""])
                        func_doc = ast.get_docstring(node)
                        if func_doc:
                            doc_lines.extend([func_doc, ""])

                if len(doc_lines) > 2:
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write("\n".join(doc_lines))

            except Exception as e: # noqa: BLE001
                pass

if __name__ == "__main__":
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    out_dir = os.path.join(root, 'docs', 'api')
    generate_docs(root, out_dir)
    print(f"Generated docs at {out_dir}")
