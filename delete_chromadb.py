"""Quick script to delete corrupted ChromaDB"""
import shutil
from pathlib import Path

chromadb_path = Path(__file__).parent / "src" / "reception" / "suggest_destination" / "chromadb"

print(f"Deleting ChromaDB at: {chromadb_path}")

if chromadb_path.exists():
    shutil.rmtree(chromadb_path)
    print("✓ ChromaDB deleted")
else:
    print("ChromaDB not found")

print("\nNow restart the reception server. ChromaDB will be recreated automatically on first request.")
