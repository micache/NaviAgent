"""
Test to verify database tables are created by Agno and check data persistence
"""

import asyncio
import os
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator_agent import TravelOrchestrator
from config.database import get_db
from schemas.request import TravelRequest


async def check_database_tables():
    """Check if Agno creates tables in the database."""
    print("=" * 80)
    print("DATABASE TABLES VERIFICATION")
    print("=" * 80)

    # Get database instance
    db = get_db()
    print(f"\n1. Database Connection:")
    print(f"   ✓ Connected to: {db.db_url.split('@')[1] if '@' in db.db_url else 'database'}")
    print(f"   ✓ Memory table: {db.memory_table}")
    print(f"   ✓ Session table: {db.session_table}")

    # Check if tables exist in database
    print(f"\n2. Checking PostgreSQL Tables:")

    try:
        # Use raw SQL to check if tables exist
        from sqlalchemy import inspect, text

        inspector = inspect(db.engine)
        all_tables = inspector.get_table_names(schema="ai")

        print(f"   Tables in 'ai' schema:")
        for table in all_tables:
            print(f"   - {table}")

        # Check specific tables
        expected_tables = ["agent_sessions", "agent_runs", "user_memories"]
        for table in expected_tables:
            if table in all_tables:
                print(f"   ✅ Table '{table}' exists")

                # Count rows
                with db.Session() as session:
                    result = session.execute(text(f"SELECT COUNT(*) FROM ai.{table}"))
                    count = result.scalar()
                    print(f"      → {count} rows")
            else:
                print(f"   ❌ Table '{table}' NOT FOUND")

    except Exception as e:
        print(f"   ❌ Error checking tables: {e}")

    # Test agent creation with database
    print(f"\n3. Testing Agent with Database:")

    try:
        # Create orchestrator with database
        user_id = "test_user_verify_tables"
        session_id = f"{user_id}_test_session"

        orchestrator = TravelOrchestrator(db=db, user_id=user_id, enable_memory=True)

        print(f"   ✓ Orchestrator created")
        print(f"   ✓ User ID: {user_id}")

        # Check if agents have database
        weather_has_db = orchestrator.weather_agent.db is not None
        print(f"   ✓ Weather agent has DB: {weather_has_db}")

        if weather_has_db:
            print(f"      → Memory table: {orchestrator.weather_agent.db.memory_table}")
            print(f"      → Session table: {orchestrator.weather_agent.db.session_table}")

    except Exception as e:
        print(f"   ❌ Error creating agent: {e}")
        import traceback

        traceback.print_exc()

    # Test simple agent run with session_id
    print(f"\n4. Testing Agent Run with Session ID:")

    try:
        from agents.weather_agent import create_weather_agent
        from models.schemas import WeatherAgentInput

        weather_agent = create_weather_agent(agent_name="test_weather", db=db, user_id=user_id)

        print(f"   ✓ Weather agent created")
        print(f"   ✓ Agent has storage: {weather_agent.storage is not None}")
        print(f"   ✓ Agent user_id: {weather_agent.user_id}")

        # Run agent with session_id
        print(f"   → Running agent with session_id: {session_id}")

        response = await weather_agent.arun(
            WeatherAgentInput(destination="Tokyo", departure_date="2025-12-15", duration_days=5),
            session_id=session_id,
        )

        print(f"   ✅ Agent ran successfully")
        print(f"   ✓ Response type: {type(response.content).__name__}")

        # Check if session was saved
        print(f"\n5. Checking if Session was Saved:")

        with db.Session() as session:
            # Check agent_sessions table
            result = session.execute(
                text(
                    "SELECT session_id, agent_id, user_id FROM ai.agent_sessions WHERE session_id = :sid"
                ),
                {"sid": session_id},
            )
            row = result.fetchone()

            if row:
                print(f"   ✅ Session found in database!")
                print(f"      → Session ID: {row[0]}")
                print(f"      → Agent ID: {row[1]}")
                print(f"      → User ID: {row[2]}")
            else:
                print(f"   ❌ Session NOT found in database")
                print(f"      → This means Agno is not saving sessions")

        # Check agent_runs table
        with db.Session() as session:
            result = session.execute(
                text("SELECT COUNT(*) FROM ai.agent_runs WHERE session_id = :sid"),
                {"sid": session_id},
            )
            count = result.scalar()
            print(f"   → Agent runs for this session: {count}")

    except Exception as e:
        print(f"   ❌ Error during agent run: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(check_database_tables())
