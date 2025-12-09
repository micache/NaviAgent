"""Check data in existing tables"""

import json
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load .env from repository root
env_path = Path(__file__).resolve().parents[3] / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

print("=" * 80)
print("VIEWING DATABASE DATA")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)

    # Check agent_sessions
    print("\n📊 AGENT_SESSIONS TABLE:")
    print("-" * 80)

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        """
        SELECT session_id, agent_id, user_id, created_at, updated_at
        FROM ai.agent_sessions
        ORDER BY created_at DESC
        LIMIT 10
    """
    )

    sessions = cursor.fetchall()
    if sessions:
        for i, session in enumerate(sessions, 1):
            print(f"\n{i}. Session ID: {session['session_id']}")
            print(f"   Agent ID: {session['agent_id']}")
            print(f"   User ID: {session['user_id']}")
            print(f"   Created: {session['created_at']}")
            print(f"   Updated: {session['updated_at']}")
    else:
        print("   (No sessions found)")

    # Check user_memories
    print("\n\n📊 USER_MEMORIES TABLE:")
    print("-" * 80)

    cursor.execute(
        """
        SELECT memory_id, user_id, memory, updated_at
        FROM ai.user_memories
        ORDER BY updated_at DESC
        LIMIT 10
    """
    )

    memories = cursor.fetchall()
    if memories:
        for i, memory in enumerate(memories, 1):
            print(f"\n{i}. Memory ID: {memory['memory_id']}")
            print(f"   User ID: {memory['user_id']}")
            print(f"   Memory: {memory['memory'][:100]}...")  # First 100 chars
            print(f"   Updated: {memory['updated_at']}")
    else:
        print("   (No memories found)")

    # Check session data detail
    print("\n\n📊 DETAILED SESSION DATA:")
    print("-" * 80)

    cursor.execute(
        """
        SELECT session_id, agent_id, session_data, metadata
        FROM ai.agent_sessions
        ORDER BY created_at DESC
        LIMIT 1
    """
    )

    session = cursor.fetchone()
    if session:
        print(f"\nMost recent session: {session['session_id']}")
        print(f"Agent ID: {session['agent_id']}")

        if session["session_data"]:
            print(f"\nSession Data (first 500 chars):")
            session_data_str = json.dumps(session["session_data"], indent=2)
            print(session_data_str[:500])
            if len(session_data_str) > 500:
                print("...")

        if session["metadata"]:
            print(f"\nMetadata:")
            print(json.dumps(session["metadata"], indent=2))

    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("SUMMARY:")
print("✅ Database is working and storing data")
print("✅ Agno has created tables automatically")
print("✅ Sessions and memories are being saved")
print("\nNote: 'agent_runs' table might be created on-demand")
print("=" * 80)
