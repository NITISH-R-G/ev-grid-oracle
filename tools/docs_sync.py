import ast
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_docs(repo_root, docs_dir):
    os.makedirs(docs_dir, exist_ok=True)

    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_root)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    tree = ast.parse(content)

                    doc_content = f"# Documentation for `{rel_path}`\n\n"

                    module_doc = ast.get_docstring(tree)
                    if module_doc:
                        doc_content += f"## Module Docstring\n\n{module_doc}\n\n"

                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            doc_content += f"## Class: `{node.name}`\n\n"
                            class_doc = ast.get_docstring(node)
                            if class_doc:
                                doc_content += f"{class_doc}\n\n"

                            for sub_node in node.body:
                                if isinstance(sub_node, ast.FunctionDef):
                                    doc_content += f"### Method: `{sub_node.name}`\n\n"
                                    method_doc = ast.get_docstring(sub_node)
                                    if method_doc:
                                        doc_content += f"{method_doc}\n\n"

                        elif isinstance(node, ast.FunctionDef) and not getattr(node, '_is_method', False):
                            # Very basic check, proper check would require parent tracking
                            doc_content += f"## Function: `{node.name}`\n\n"
                            func_doc = ast.get_docstring(node)
                            if func_doc:
                                doc_content += f"{func_doc}\n\n"


                    safe_name = rel_path.replace('/', '_').replace('\\', '_').replace('.py', '.md')
                    doc_path = os.path.join(docs_dir, safe_name)

                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(doc_content)

                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")

if __name__ == "__main__":
    generate_docs('.', 'docs')