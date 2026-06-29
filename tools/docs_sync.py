import os


def sync_docs(docs_dir="docs"):
    index_path = os.path.join(docs_dir, "index.md")

    markdown_files = []
    for root, _, files in os.walk(docs_dir):
        for file in files:
            if file.endswith(".md") and file != "index.md":
                rel_path = os.path.relpath(os.path.join(root, file), docs_dir)
                markdown_files.append(rel_path)

    markdown_files.sort()

    os.makedirs(docs_dir, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("# Documentation Index\n\n")
        f.write("This index is automatically generated.\n\n")
        for file in markdown_files:
            title = file.replace(".md", "").replace("_", " ").title()
            f.write(f"* [{title}]({file})\n")


if __name__ == "__main__":
    sync_docs()
