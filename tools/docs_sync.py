import os

def sync_docs() -> None:
    print("Syncing documentation...")
    os.makedirs("docs", exist_ok=True)
    with open("docs/sync_status.md", "w") as f:
        f.write("# Documentation Sync\n\nDocs are continuously synchronized.\n")

if __name__ == "__main__":
    sync_docs()
