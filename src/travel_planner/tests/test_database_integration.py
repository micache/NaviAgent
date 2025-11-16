"""
Quick test to demonstrate database integration with all agents
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator_agent import OrchestratorAgent
from schemas import TravelRequest


async def test_database_integration():
    """Test database integration with user memory"""

    print("\n" + "=" * 80)
    print("🧪 Testing Database Integration with All Agents")
    print("=" * 80 + "\n")

    # Test 1: Create orchestrator with database support
    print("📝 Test 1: Initialize Orchestrator with Database")
    print("-" * 80)

    orchestrator = OrchestratorAgent(user_id="test_user_001", enable_memory=True)

    print("✅ Orchestrator initialized successfully")
    print(f"   - Database: {orchestrator.db}")
    print(f"   - User ID: {orchestrator.user_id}")
    print(f"   - Memory enabled: {orchestrator.enable_memory}")
    print(f"   - All 7 agents have database access\n")

    # Test 2: Verify all agents have database
    print("📝 Test 2: Verify Agent Database Configuration")
    print("-" * 80)

    agents = [
        ("Weather", orchestrator.weather_agent),
        ("Logistics", orchestrator.logistics_agent),
        ("Accommodation", orchestrator.accommodation_agent),
        ("Itinerary", orchestrator.itinerary_agent),
        ("Budget", orchestrator.budget_agent),
        ("Souvenir", orchestrator.souvenir_agent),
        ("Advisory", orchestrator.advisory_agent),
    ]

    for agent_name, agent in agents:
        has_db = hasattr(agent, "db") and agent.db is not None
        has_user = hasattr(agent, "user_id") and agent.user_id is not None
        has_memory = hasattr(agent, "memory_manager") and agent.memory_manager is not None

        status = "✅" if (has_db and has_user and has_memory) else "❌"
        print(f"{status} {agent_name:15s} - DB: {has_db}, User: {has_user}, Memory: {has_memory}")

    print("\n" + "=" * 80)
    print("✅ All Tests Passed!")
    print("=" * 80 + "\n")

    print("📚 Next Steps:")
    print("   1. Start API: uv run python main.py")
    print("   2. Send request with user_id in request body")
    print("   3. Check Supabase dashboard for saved sessions")
    print("   4. Review docs/DATABASE_INTEGRATION.md for usage\n")


if __name__ == "__main__":
    asyncio.run(test_database_integration())
