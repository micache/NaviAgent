import argparse

from reception.suggest_destination.config.config import config
from reception.suggest_destination.retrieval import RetrievalSystem


def main():
    parser = argparse.ArgumentParser(description="Index dataset into ChromaDB")
    parser.add_argument(
        "--data", type=str, default=str(config.paths.data_path), help="Path to CSV file"
    )
    parser.add_argument(
        "--collection", type=str, default=config.index.collection_name, help="Collection name"
    )
    parser.add_argument(
        "--batch-size", type=int, default=config.index.batch_size, help="Batch size for indexing"
    )
    parser.add_argument("--reset", action="store_true", help="Reset collection before indexing")

    args = parser.parse_args()

    print("=" * 80)
    print("INDEXING DATASET")
    print("=" * 80)
    print(f"Data: {args.data}")
    print(f"Collection: {args.collection}")
    print(f"Batch size: {args.batch_size}")
    print(f"Reset: {args.reset}")
    print("=" * 80)

    retrieval = RetrievalSystem()
    retrieval.create_collection(collection_name=args.collection, reset=args.reset)
    retrieval.index_dataset(csv_path=args.data, batch_size=args.batch_size)

    print("\n✓ Indexing completed!")


if __name__ == "__main__":
    main()
