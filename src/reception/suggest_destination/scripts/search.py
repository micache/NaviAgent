# scripts/search.py

import argparse
from retrieval import RetrievalSystem
from config.config import config


def main():
    parser = argparse.ArgumentParser(description="Search for similar destinations")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--top-k", type=int, default=config.search.top_k,
                       help="Number of results")
    parser.add_argument("--collection", type=str, default=config.search.collection_name,
                       help="Collection name")
    parser.add_argument("--group", action="store_true",
                       help="Group results by destination (show unique destinations only)")
    parser.add_argument("--aggregate", action="store_true",
                       help="Show aggregated results with all descriptions per destination")
    
    args = parser.parse_args()
    
    retrieval = RetrievalSystem()
    retrieval.create_collection(collection_name=args.collection)
    
    if args.aggregate:
        # Aggregated view: show all descriptions per destination
        aggregated = retrieval.search_with_aggregation(args.query, k=args.top_k)
        RetrievalSystem.print_aggregated_results(aggregated, query=args.query)
    else:
        # Normal or grouped view
        results = retrieval.search(args.query, k=args.top_k, group_by_destination=args.group)
        RetrievalSystem.print_results(results, query=args.query)


if __name__ == "__main__":
    main()