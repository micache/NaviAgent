"""
Test DuckDuckGo search functionality
"""

import asyncio

from tools.search_tool import search_tools


async def test_search():
    """Test various search queries"""

    test_queries = [
        "Japan best souvenirs",
        "Tokyo weather December 2025",
        "Japan travel visa requirements",
        "Kyoto tourist attractions",
        "Japan local food recommendations",
    ]

    print("=" * 80)
    print("Testing DuckDuckGo Search Tool")
    print("=" * 80)

    for i, query in enumerate(test_queries, 1):
        print(f"\n[Test {i}/{len(test_queries)}] Query: '{query}'")
        print("-" * 80)

        try:
            result = search_tools.duckduckgo_search(query=query, max_results=3)

            if "[Search" in result:
                print("⚠️  FALLBACK MODE - No live results")
                print(result[:200] + "...")
            else:
                print("✅ SUCCESS - Got results:")
                # Show first 300 chars
                print(result[:300] + "...")

        except Exception as e:
            print(f"❌ ERROR: {e}")

        print()

    print("=" * 80)
    print("Test Complete")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_search())
