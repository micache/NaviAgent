"""Simple database check - verify if Agno creates tables"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import get_db
from sqlalchemy import inspect, text


def check_tables():
    """Check if tables exist in database."""
    print("=" * 80)
    print("CHECKING DATABASE TABLES")
    print("=" * 80)

    db = get_db()
    print(f"\n1. Database URL: {db.db_url.split('@')[1]}")
    print(f"   Memory table: {db.memory_table_name}")
    print(f"   Session table: {db.session_table_name}")

    print(f"\n2. Checking tables in 'ai' schema:")
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names(schema="ai")

        if tables:
            print(f"   Found {len(tables)} tables:")
            for table in tables:
                # Count rows
                with db.Session() as session:
                    result = session.execute(text(f"SELECT COUNT(*) FROM ai.{table}"))
                    count = result.scalar()
                    print(f"   - {table}: {count} rows")
        else:
            print("   NO TABLES FOUND IN 'ai' SCHEMA")
            print("   -> Agno has NOT created any tables yet")

        # Check if expected tables exist
        expected = ["agent_sessions", "agent_runs", "user_memories"]
        for table in expected:
            if table in tables:
                print(f"   ✅ {table} exists")
            else:
                print(f"   ❌ {table} NOT FOUND (Agno should create this)")

    except Exception as e:
        print(f"   Error: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    check_tables()
