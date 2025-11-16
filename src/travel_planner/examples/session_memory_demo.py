"""
Example: Agent với session và memory management
Demonstrates how to use PostgreSQL database for chat history and user memories
"""

import asyncio
from datetime import date

from agno.agent import Agent
from config.database import get_db
from config.model_settings import model_settings
from rich.pretty import pprint


async def demo_basic_session():
    """Demo 1: Basic session with chat history."""
    print("\n" + "=" * 80)
    print("DEMO 1: Basic Session with Chat History")
    print("=" * 80)

    db = get_db()

    # Create agent with session support
    agent = Agent(
        model=model_settings.create_model_for_agno("demo"),
        db=db,
        add_history_to_context=True,  # Add previous messages to context
        num_history_runs=5,  # Include last 5 runs
        description="You are a helpful travel assistant.",
        markdown=True,
    )

    user_id = "test_user_001"
    session_id = "session_travel_001"

    # First message
    print("\n🔹 User: What are the best places to visit in Japan?")
    response1 = agent.run(
        "What are the best places to visit in Japan?",
        user_id=user_id,
        session_id=session_id,
    )
    print(f"🤖 Agent: {response1.content[:200]}...")

    # Second message - agent should remember previous context
    print("\n🔹 User: How many days should I spend there?")
    response2 = agent.run(
        "How many days should I spend there?", user_id=user_id, session_id=session_id
    )
    print(f"🤖 Agent: {response2.content[:200]}...")

    # Third message - agent remembers entire conversation
    print("\n🔹 User: What was my first question?")
    response3 = agent.run("What was my first question?", user_id=user_id, session_id=session_id)
    print(f"🤖 Agent: {response3.content}")

    print(f"\n✅ Session ID: {session_id}")
    print(f"✅ Total runs: 3")


async def demo_user_memory():
    """Demo 2: User memory - remembers user preferences across sessions."""
    print("\n" + "=" * 80)
    print("DEMO 2: User Memory - Persistent Across Sessions")
    print("=" * 80)

    db = get_db()

    # Create agent with memory support
    agent = Agent(
        model=model_settings.create_model_for_agno("demo"),
        db=db,
        enable_user_memories=True,  # Automatic memory management
        add_history_to_context=True,
        num_history_runs=3,
        description="You are a helpful travel assistant that remembers user preferences.",
        markdown=True,
    )

    user_id = "john_doe_123"

    # Session 1: User shares preferences
    print("\n📍 SESSION 1: User shares preferences")
    session_1 = "memory_session_001"

    print("🔹 User: My name is John and I love beach destinations and seafood.")
    agent.run(
        "My name is John and I love beach destinations and seafood.",
        user_id=user_id,
        session_id=session_1,
    )

    print("🔹 User: I have a budget of $3000 and prefer 5-star hotels.")
    agent.run(
        "I have a budget of $3000 and prefer 5-star hotels.",
        user_id=user_id,
        session_id=session_1,
    )

    # Check stored memories
    print("\n💾 Stored memories:")
    memories = agent.get_user_memories(user_id=user_id)
    for memory in memories:
        print(f"   • {memory.memory}")

    # Session 2: New session - agent should remember preferences
    print("\n📍 SESSION 2: New conversation (different session)")
    session_2 = "memory_session_002"

    print("🔹 User: Can you recommend a destination for my next trip?")
    response = agent.run(
        "Can you recommend a destination for my next trip?",
        user_id=user_id,
        session_id=session_2,
    )
    print(f"🤖 Agent: {response.content[:300]}...")
    print("\n✅ Agent remembered: name, preferences (beach/seafood), budget, hotel preference")


async def demo_multi_user():
    """Demo 3: Multiple users with separate sessions."""
    print("\n" + "=" * 80)
    print("DEMO 3: Multi-User Sessions")
    print("=" * 80)

    db = get_db()

    agent = Agent(
        model=model_settings.create_model_for_agno("demo"),
        db=db,
        add_history_to_context=True,
        num_history_runs=3,
        enable_user_memories=True,
        markdown=True,
    )

    # User 1
    user_1_id = "alice_001"
    session_1_id = "alice_session_001"

    print("\n👤 USER 1 (Alice):")
    print("🔹 I love mountain hiking and adventure sports")
    agent.run(
        "I love mountain hiking and adventure sports",
        user_id=user_1_id,
        session_id=session_1_id,
    )

    # User 2
    user_2_id = "bob_002"
    session_2_id = "bob_session_001"

    print("\n👤 USER 2 (Bob):")
    print("🔹 I prefer relaxing beach resorts and spa treatments")
    agent.run(
        "I prefer relaxing beach resorts and spa treatments",
        user_id=user_2_id,
        session_id=session_2_id,
    )

    # Ask for recommendations
    print("\n📍 Asking both users for recommendations:")

    print("\n👤 USER 1 (Alice): Recommend a destination for me")
    response_1 = agent.run(
        "Recommend a destination for me", user_id=user_1_id, session_id=session_1_id
    )
    print(f"🤖 Agent: {response_1.content[:150]}... (should mention mountains/adventure)")

    print("\n👤 USER 2 (Bob): Recommend a destination for me")
    response_2 = agent.run(
        "Recommend a destination for me", user_id=user_2_id, session_id=session_2_id
    )
    print(f"🤖 Agent: {response_2.content[:150]}... (should mention beach/spa)")

    print("\n✅ Each user has isolated memories and sessions")


async def demo_session_summary():
    """Demo 4: Session summaries for long conversations."""
    print("\n" + "=" * 80)
    print("DEMO 4: Session Summaries")
    print("=" * 80)

    db = get_db()

    agent = Agent(
        model=model_settings.create_model_for_agno("demo"),
        db=db,
        enable_session_summaries=True,  # Enable automatic summaries
        add_history_to_context=True,
        num_history_runs=5,
        markdown=True,
    )

    user_id = "summary_user"
    session_id = "long_conversation_001"

    print("\n💬 Having a long conversation...")

    messages = [
        "I want to plan a 10-day trip to Europe",
        "I'm interested in visiting Paris, Rome, and Barcelona",
        "What's the best time of year to go?",
        "Can you suggest good hotels in each city?",
        "What about local food I should try?",
    ]

    for i, msg in enumerate(messages, 1):
        print(f"\n🔹 Message {i}: {msg}")
        agent.run(msg, user_id=user_id, session_id=session_id)

    # Get session summary
    summary = agent.get_session_summary(session_id=session_id)
    print("\n📝 Session Summary:")
    print(f"   {summary.summary}")

    print("\n✅ Summary created automatically after conversation")


async def demo_memory_management():
    """Demo 5: Manual memory management."""
    print("\n" + "=" * 80)
    print("DEMO 5: Memory Management Operations")
    print("=" * 80)

    db = get_db()

    user_id = "memory_test_user"

    # Add memories manually
    print("\n➕ Adding memories manually:")
    db.upsert_user_memory(
        user_id=user_id, memory="User prefers vegetarian food", input="I'm vegetarian"
    )
    db.upsert_user_memory(
        user_id=user_id, memory="User has motion sickness", input="I get car sick easily"
    )
    db.upsert_user_memory(
        user_id=user_id,
        memory="User travels with 2 kids aged 5 and 8",
        input="I have two kids",
    )

    # List memories
    print("\n📋 Current memories:")
    memories = db.get_user_memories(user_id=user_id)
    for i, memory in enumerate(memories, 1):
        print(f"   {i}. {memory.memory}")

    # Delete a specific memory
    print("\n🗑️  Deleting memory about motion sickness...")
    memory_to_delete = next(m for m in memories if "motion sickness" in m.memory)
    db.delete_user_memory(memory_id=memory_to_delete.memory_id)

    # List again
    print("\n📋 After deletion:")
    memories = db.get_user_memories(user_id=user_id)
    for i, memory in enumerate(memories, 1):
        print(f"   {i}. {memory.memory}")

    # Clear all memories for user
    print("\n🧹 Clearing all memories for user...")
    db.clear_memories(user_id=user_id)

    memories = db.get_user_memories(user_id=user_id)
    print(f"✅ Memories after clear: {len(memories)}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("AGENT SESSION & MEMORY DEMOS")
    print("=" * 80)

    # await demo_basic_session()
    # await demo_user_memory()
    # await demo_multi_user()
    # await demo_session_summary()
    await demo_memory_management()

    print("\n" + "=" * 80)
    print("ALL DEMOS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
