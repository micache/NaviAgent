"""Direct database check using psycopg2"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 80)
print("DIRECT DATABASE CHECK - PSYCOPG2")
print("=" * 80)

try:
    # Connect to database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    print(f"\n✅ Connected to database")

    # Check if 'ai' schema exists
    cursor.execute(
        """
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name = 'ai'
    """
    )
    schema_exists = cursor.fetchone()

    if schema_exists:
        print(f"✅ Schema 'ai' exists")
    else:
        print(f"❌ Schema 'ai' NOT FOUND")
        print(f"   -> Agno has not created the schema yet")

    # List all tables in 'ai' schema
    cursor.execute(
        """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai'
        ORDER BY table_name
    """
    )

    tables = cursor.fetchall()

    if tables:
        print(f"\n📊 Found {len(tables)} tables in 'ai' schema:")
        for table in tables:
            table_name = table[0]
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM ai.{table_name}")
            count = cursor.fetchone()[0]
            print(f"   - {table_name}: {count} rows")
    else:
        print(f"\n❌ NO TABLES in 'ai' schema")
        print(f"   -> Agno framework has NOT created any tables")
        print(f"   -> This means database integration is not working")

    # Check expected Agno tables
    expected_tables = ["agent_sessions", "agent_runs", "user_memories"]
    print(f"\n🔍 Checking for expected Agno tables:")

    table_names = [t[0] for t in tables] if tables else []

    for expected in expected_tables:
        if expected in table_names:
            print(f"   ✅ {expected} - EXISTS")
        else:
            print(f"   ❌ {expected} - NOT FOUND")
            print(f"      → Agno should auto-create this when agent runs")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("CONCLUSION:")
if not tables:
    print("❌ Agno is NOT creating tables in the database")
    print("   Possible reasons:")
    print("   1. Agents are not being run with session_id")
    print("   2. Database permissions issue")
    print("   3. Agno not configured to auto-create tables")
    print("   4. Need to manually create tables first")
else:
    print("✅ Database integration is working")
print("=" * 80)
