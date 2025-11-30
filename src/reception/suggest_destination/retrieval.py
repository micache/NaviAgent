from typing import Dict, List

import chromadb
import pandas as pd
from tqdm import tqdm

from reception.suggest_destination.config.config import config
from reception.suggest_destination.embedding import EmbeddingGenerator


class RetrievalSystem:
    """ChromaDB-based retrieval system"""

    def __init__(self, chromadb_path: str = None):
        chromadb_path = chromadb_path or str(config.paths.chromadb_path)
        self.client = chromadb.PersistentClient(path=chromadb_path)
        self.collection = None
        self.embedding_generator = EmbeddingGenerator()

    def create_collection(self, collection_name: str = None, reset: bool = False):
        """Create or load collection"""
        collection_name = collection_name or config.index.collection_name

        if reset:
            try:
                self.client.delete_collection(collection_name)
                print(f"Deleted existing collection: {collection_name}")
            except:
                pass

        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"✓ Loaded collection: {collection_name} ({self.collection.count()} docs)")
        except:
            self.collection = self.client.create_collection(
                name=collection_name, metadata={"hnsw:space": "cosine"}
            )
            print(f"✓ Created collection: {collection_name}")

    def index_dataset(self, csv_path: str = None, batch_size: int = None):
        """Index dataset into ChromaDB

        Strategy: Store description in metadata, use destination as document.
        This allows multiple descriptions per destination.

        Uses batch processing for speed optimization.
        """
        csv_path = csv_path or str(config.paths.data_path)
        batch_size = batch_size or config.index.batch_size

        df = pd.read_csv(csv_path)
        print(f"Loading {len(df)} records from {csv_path}")

        if self.collection is None:
            self.create_collection()

        for i in tqdm(range(0, len(df), batch_size), desc="Indexing"):
            batch = df.iloc[i : i + batch_size]

            # Prepare batch data
            batch_texts = []
            valid_rows = []

            for idx, row in batch.iterrows():
                description = str(row["description"]).strip()
                destination = str(row["destination"]).strip()

                if not description or description == "nan":
                    continue

                batch_texts.append(description)
                valid_rows.append((idx, destination))

            if not batch_texts:
                continue

            try:
                # Generate embeddings in batch - MUCH FASTER
                embeddings_array = self.embedding_generator.generate_batch(batch_texts)

                # Prepare for ChromaDB
                embeddings = embeddings_array.tolist()
                documents = [dest for _, dest in valid_rows]
                metadatas = [
                    {"description": desc, "row_id": int(idx)}
                    for (idx, _), desc in zip(valid_rows, batch_texts)
                ]
                ids = [f"doc_{idx}" for idx, _ in valid_rows]

                # Add to collection
                self.collection.add(
                    embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
                )

            except Exception as e:
                print(f"Error processing batch at index {i}: {e}")
                # Fallback to one-by-one processing for this batch
                for (idx, destination), description in zip(valid_rows, batch_texts):
                    try:
                        emb = self.embedding_generator.generate(description)
                        self.collection.add(
                            embeddings=[emb.tolist()],
                            documents=[destination],
                            metadatas=[{"description": description, "row_id": int(idx)}],
                            ids=[f"doc_{idx}"],
                        )
                    except Exception as e2:
                        print(f"Error at row {idx}: {e2}")

        print(f"✓ Indexed {self.collection.count()} documents")

    def search(self, query: str, k: int = None, group_by_destination: bool = False) -> List[Dict]:
        """Search for top-K similar documents

        Args:
            query: Search query
            k: Number of results
            group_by_destination: If True, group results by destination and keep best match
        """
        k = k or config.search.top_k

        if self.collection is None:
            self.create_collection()

        # Generate query embedding (đã normalized trong model)
        query_embedding = self.embedding_generator.generate(query)

        # Fetch more results if grouping (để có đủ unique destinations)
        fetch_k = k * 5 if group_by_destination else k

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()], n_results=fetch_k
        )

        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append(
                {
                    "rank": i + 1,
                    "destination": results["documents"][0][i],  # destination là document
                    "description": results["metadatas"][0][i][
                        "description"
                    ],  # description trong metadata
                    "similarity": 1 - results["distances"][0][i],
                    "distance": results["distances"][0][i],
                    "row_id": results["metadatas"][0][i]["row_id"],
                }
            )

        # Group by destination if requested
        if group_by_destination:
            seen_destinations = {}
            grouped = []

            for result in formatted:
                dest = result["destination"]
                if dest not in seen_destinations:
                    seen_destinations[dest] = result
                    grouped.append(result)

                    if len(grouped) >= k:
                        break

            # Re-rank
            for i, item in enumerate(grouped, 1):
                item["rank"] = i

            return grouped

        return formatted[:k]

    @staticmethod
    def print_results(results: List[Dict], query: str = None, show_row_id: bool = False):
        """Pretty print search results"""
        print("\n" + "=" * 80)
        if query:
            print(f"QUERY: {query}")
            print("=" * 80)

        for r in results:
            print(f"\n[{r['rank']}] {r['destination']} (similarity: {r['similarity']:.4f})")
            print(f"    {r['description'][:120]}...")
            if show_row_id:
                print(f"    [row_id: {r['row_id']}]")
            print("-" * 80)

    def search_with_aggregation(self, query: str, k: int = None) -> Dict:
        """Search and return aggregated results by destination

        Returns both grouped (unique destinations) and all results
        """
        k = k or config.search.top_k

        # Get all results
        all_results = self.search(query, k=k * 5, group_by_destination=False)

        # Group by destination with all matching descriptions
        destination_groups = {}
        for result in all_results:
            dest = result["destination"]
            if dest not in destination_groups:
                destination_groups[dest] = {
                    "destination": dest,
                    "best_similarity": result["similarity"],
                    "descriptions": [],
                }
            destination_groups[dest]["descriptions"].append(
                {
                    "description": result["description"],
                    "similarity": result["similarity"],
                    "row_id": result["row_id"],
                }
            )

        # Sort by best similarity
        grouped_list = sorted(
            destination_groups.values(), key=lambda x: x["best_similarity"], reverse=True
        )[:k]

        return {"grouped": grouped_list, "all_results": all_results[: k * 3]}

    @staticmethod
    def print_aggregated_results(aggregated: Dict, query: str = None):
        """Print aggregated results with all descriptions per destination"""
        print("\n" + "=" * 80)
        if query:
            print(f"QUERY: {query}")
            print("=" * 80)
        print("GROUPED BY DESTINATION")
        print("=" * 80)

        for i, group in enumerate(aggregated["grouped"], 1):
            print(f"\n[{i}] 📍 {group['destination']}")
            print(f"    Best similarity: {group['best_similarity']:.4f}")
            print(f"    Matching descriptions ({len(group['descriptions'])}):")

            for j, desc in enumerate(group["descriptions"][:3], 1):  # Show top 3
                print(f"      {j}. [{desc['similarity']:.3f}] {desc['description'][:80]}...")

            if len(group["descriptions"]) > 3:
                print(f"      ... and {len(group['descriptions']) - 3} more")

            print("-" * 80)
