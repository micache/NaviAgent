"""Check ChromaDB status"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from reception.suggest_destination.config.config import config
from reception.suggest_destination.retrieval import RetrievalSystem

chromadb_path = config.paths.chromadb_path

print("=" * 60)
print("CHROMADB STATUS CHECK")
print("=" * 60)

print(f"\nChromaDB path: {chromadb_path}")
print(f"Exists: {chromadb_path.exists()}")

if chromadb_path.exists():
    try:
        retrieval = RetrievalSystem()
        collection = retrieval.client.get_collection(config.index.collection_name)
        count = collection.count()
        
        print(f"\n✅ Collection '{config.index.collection_name}' found")
        print(f"   Documents indexed: {count}")
        
        # Test a query
        test_query = "beautiful beach"
        results = retrieval.search(test_query, k=3)
        print(f"\n✅ Search works! Found {len(results)} results for: '{test_query}'")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nChromaDB exists but may be corrupted or empty.")
        print("Solution: Send a request to the API to auto-create index.")
else:
    print("\n⚠️  ChromaDB not found")
    print("Solution: Send a request to the API to auto-create index.")

print("\n" + "=" * 60)
