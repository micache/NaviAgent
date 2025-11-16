"""
Test DuckDuckGo với Agno trực tiếp theo documentation
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

print("=" * 80)
print("Test 1: DuckDuckGo với DeepSeek (như documentation)")
print("=" * 80)

try:
    from agno.agent import Agent
    from agno.models.deepseek import DeepSeek
    from agno.tools.duckduckgo import DuckDuckGoTools

    agent = Agent(
        model=DeepSeek(id="deepseek-chat"),
        tools=[DuckDuckGoTools()],
        markdown=True,
    )

    print("\n✅ Agent created successfully")
    print("🔍 Testing search with query: 'What are popular souvenirs in Japan?'\n")

    agent.print_response("What are popular souvenirs in Japan?")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()


print("\n" + "=" * 80)
print("Test 2: Direct ddgs package test")
print("=" * 80)

try:
    from ddgs import DDGS

    print("\n🔍 Testing direct ddgs.text() call...")

    ddgs = DDGS()
    results = ddgs.text("Japan souvenirs", max_results=3)

    print(f"\n✅ Got results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'No title')}")
        print(f"   URL: {result.get('href', 'No URL')}")
        print(f"   Snippet: {result.get('body', 'No description')[:100]}...")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()


print("\n" + "=" * 80)
print("Test 3: Check ddgs version and configuration")
print("=" * 80)

try:
    import ddgs

    print(f"\n📦 ddgs version: {ddgs.__version__ if hasattr(ddgs, '__version__') else 'Unknown'}")

    from ddgs import DDGS

    # Try with different parameters
    print("\n🔍 Testing with backend='html'...")
    ddgs = DDGS()
    results = list(ddgs.text("Japan", backend="html", max_results=2))
    print(f"✅ HTML backend: Got {len(results)} results")

    print("\n🔍 Testing with backend='api'...")
    ddgs = DDGS()
    results = list(ddgs.text("Japan", backend="api", max_results=2))
    print(f"✅ API backend: Got {len(results)} results")

    print("\n🔍 Testing with backend='lite'...")
    ddgs = DDGS()
    results = list(ddgs.text("Japan", backend="lite", max_results=2))
    print(f"✅ Lite backend: Got {len(results)} results")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()


print("\n" + "=" * 80)
print("Test 4: Check network and proxy settings")
print("=" * 80)

try:
    import httpx

    print("\n🌐 Testing network connectivity...")

    # Test direct access to DuckDuckGo
    response = httpx.get("https://duckduckgo.com", timeout=10)
    print(f"✅ DuckDuckGo accessible: Status {response.status_code}")

    # Test with headers
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = httpx.get("https://duckduckgo.com", headers=headers, timeout=10)
    print(f"✅ DuckDuckGo with headers: Status {response.status_code}")

except Exception as e:
    print(f"\n❌ Network Error: {e}")


print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
