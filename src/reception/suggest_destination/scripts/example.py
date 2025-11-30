from reception.suggest_destination.retrieval import RetrievalSystem
from reception.suggest_destination.config.config import config

def interactive_search():
    """Interactive search interface"""
    print("="*80)
    print("DESTINATION SEARCH SYSTEM")
    print("="*80)
    
    retrieval = RetrievalSystem()
    retrieval.create_collection()
    
    print("\nType 'exit' or 'quit' to stop")
    print("-"*80)
    
    while True:
        query = input("\nEnter your query: ").strip()
        
        if query.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        results = retrieval.search(query)
        RetrievalSystem.print_results(results, query=query)

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        # Command line query
        query = " ".join(sys.argv[1:])
        retrieval = RetrievalSystem()
        retrieval.create_collection()
        results = retrieval.search(query)
        RetrievalSystem.print_results(results, query=query)
    else:
        # Interactive mode
        interactive_search()

if __name__ == "__main__":
    main()