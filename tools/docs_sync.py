import os
import ast

def generate_docs(src_dir, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for root, dirs, files in os.walk(src_dir):
        # Exclude hidden directories explicitly
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, src_dir)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())

                    doc_filename = rel_path.replace(os.sep, '_').replace('.py', '.md')
                    doc_filepath = os.path.join(dest_dir, doc_filename)

                    with open(doc_filepath, 'w', encoding='utf-8') as f:
                        f.write(f"# Documentation for {rel_path}\n\n")
                        module_doc = ast.get_docstring(tree)
                        if module_doc:
                            f.write(f"## Module Overview\n\n{module_doc}\n\n")

                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                f.write(f"### Class: {node.name}\n\n")
                                cls_doc = ast.get_docstring(node)
                                if cls_doc:
                                    f.write(f"{cls_doc}\n\n")
                            elif isinstance(node, ast.FunctionDef):
                                f.write(f"#### Function: {node.name}\n\n")
                                func_doc = ast.get_docstring(node)
                                if func_doc:
                                    f.write(f"{func_doc}\n\n")
                except Exception as e:
                    print(f"Failed to process {filepath}: {e}")

if __name__ == '__main__':
    generate_docs('.', 'docs/api')
