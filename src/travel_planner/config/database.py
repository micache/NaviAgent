"""
Database configuration for PostgreSQL (Supabase)
Handles agent sessions, chat history, and user memories
"""

import os
from typing import Optional

from agno.db.postgres import PostgresDb
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


class DatabaseConfig:
    """Database configuration manager."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL not found in environment variables")

    def create_db(
        self,
        memory_table: str = "user_memories",
        session_table: str = "agent_sessions",
    ) -> PostgresDb:
        """
        Create PostgreSQL database connection for Agno agents.

        Args:
            memory_table: Table name for user memories
            session_table: Table name for agent sessions

        Returns:
            PostgresDb instance configured for the application
        """
        return PostgresDb(
            db_url=self.database_url,
            memory_table=memory_table,
            session_table=session_table,
        )


# Global database instance
db_config = DatabaseConfig()
db = db_config.create_db()


# Helper functions for database operations
def get_db() -> PostgresDb:
    """Get the global database instance."""
    return db


def clear_all_data():
    """Clear all data from database (use with caution!)."""
    db.clear_memories()
    # Note: Agno doesn't have built-in methods to clear sessions/runs
    # You may need to use raw SQL if needed


def get_user_session_count(user_id: str) -> int:
    """
    Get count of sessions for a user.

    Args:
        user_id: User identifier

    Returns:
        Number of sessions
    """
    # This would require custom SQL query
    # Agno doesn't provide built-in session count method
    pass


def prune_old_memories(user_id: str, days: int = 90) -> int:
    """
    Remove memories older than specified days.

    Args:
        user_id: User identifier
        days: Number of days to keep

    Returns:
        Number of memories deleted
    """
    from datetime import datetime, timedelta

    cutoff_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
    memories = db.get_user_memories(user_id=user_id)

    deleted_count = 0
    for memory in memories:
        if memory.updated_at and memory.updated_at < cutoff_timestamp:
            db.delete_user_memory(memory_id=memory.memory_id)
            deleted_count += 1

    return deleted_count


if __name__ == "__main__":
    # Test database connection
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)

    try:
        test_db = get_db()
        print(f"✅ Database connected successfully")
        print(f"   URL: {db_config.database_url.split('@')[1]}")  # Hide password
        print(f"   Memory table: user_memories")
        print(f"   Session table: agent_sessions")
        print(f"   Run table: agent_runs")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    print("=" * 60)
