import os
import ast

def generate_docs(root_dir: str, output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Exclude hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]

        for filename in filenames:
            if filename.endswith('.py'):
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, root_dir)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        source = f.read()

                    tree = ast.parse(source)

                    # Safe filename construction based on relative path
                    safe_filename = rel_path.replace(os.sep, '_')[:-3] + '.md'
                    out_filepath = os.path.join(output_dir, safe_filename)

                    with open(out_filepath, 'w', encoding='utf-8') as out_f:
                        out_f.write(f"# Documentation for `{rel_path}`\n\n")

                        module_doc = ast.get_docstring(tree)
                        if module_doc:
                            out_f.write(f"## Module Docstring\n\n{module_doc}\n\n")

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                out_f.write(f"### Class `{node.name}`\n\n")
                                doc = ast.get_docstring(node)
                                if doc:
                                    out_f.write(f"{doc}\n\n")
                                else:
                                    out_f.write("No documentation available.\n\n")
                            elif isinstance(node, ast.FunctionDef):
                                out_f.write(f"### Function `{node.name}`\n\n")
                                doc = ast.get_docstring(node)
                                if doc:
                                    out_f.write(f"{doc}\n\n")
                                else:
                                    out_f.write("No documentation available.\n\n")
                except Exception as e:
                    print(f"Error parsing {filepath}: {e}")

if __name__ == "__main__":
    generate_docs(".", "docs/api/")
