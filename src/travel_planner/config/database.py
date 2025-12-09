"""
Database configuration for PostgreSQL (Supabase)
Handles agent sessions, chat history, and user memories
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agno.db.postgres import PostgresDb
from agno.db.schemas.memory import UserMemory
from dotenv import load_dotenv


# Load environment variables from root .env (outside travel_planner) with fallback
def _find_env_file() -> Path | None:
    candidates = [
        Path(__file__).resolve().parents[3] / ".env",  # repository root
        Path(__file__).resolve().parents[2] / ".env",  # src/.env (fallback)
        Path(__file__).parent.parent / ".env",  # travel_planner/.env (last resort)
    ]
    for path in candidates:
        if path.exists():
            return path
    return None


env_path = _find_env_file()
if env_path:
    load_dotenv(env_path, override=True)
    print(f"[DatabaseConfig] Loaded environment from {env_path}")
else:
    print("[DatabaseConfig] No .env file found; using existing environment")


class SafePostgresDb(PostgresDb):
    """PostgresDb wrapper that ignores unexpected columns (e.g., created_at)."""

    @staticmethod
    def _sanitize_memory_dict(memory_raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not memory_raw:
            return {}
        sanitized = dict(memory_raw)
        sanitized.pop("created_at", None)
        return sanitized

    def get_user_memory(
        self,
        memory_id: str,
        deserialize: bool | None = True,
        user_id: str | None = None,
    ) -> UserMemory | Dict[str, Any] | None:
        memory_raw = super().get_user_memory(
            memory_id, deserialize=False, user_id=user_id
        )
        if memory_raw is None:
            return None

        memory_raw = self._sanitize_memory_dict(memory_raw)
        if not deserialize:
            return memory_raw

        return UserMemory.from_dict(memory_raw)

    def get_user_memories(
        self,
        user_id: str | None = None,
        agent_id: str | None = None,
        team_id: str | None = None,
        topics: List[str] | None = None,
        search_content: str | None = None,
        limit: int | None = None,
        page: int | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
        deserialize: bool | None = True,
    ) -> List[UserMemory] | Tuple[List[Dict[str, Any]], int]:
        memories_raw, total_count = super().get_user_memories(
            user_id=user_id,
            agent_id=agent_id,
            team_id=team_id,
            topics=topics,
            search_content=search_content,
            limit=limit,
            page=page,
            sort_by=sort_by,
            sort_order=sort_order,
            deserialize=False,
        )

        sanitized = [self._sanitize_memory_dict(memory) for memory in memories_raw]
        if not deserialize:
            return sanitized, total_count

        return [UserMemory.from_dict(memory) for memory in sanitized]

    def upsert_user_memory(
        self, memory: UserMemory, deserialize: bool | None = True
    ) -> UserMemory | Dict[str, Any] | None:
        memory_raw = super().upsert_user_memory(memory, deserialize=False)
        if memory_raw is None:
            return None

        memory_raw = self._sanitize_memory_dict(memory_raw)
        if not deserialize:
            return memory_raw

        return UserMemory.from_dict(memory_raw)

    def upsert_memories(
        self,
        memories: List[UserMemory],
        deserialize: bool | None = True,
        preserve_updated_at: bool = False,
    ) -> List[UserMemory] | List[Dict[str, Any]]:
        raw_results = super().upsert_memories(
            memories,
            deserialize=False,
            preserve_updated_at=preserve_updated_at,
        )

        sanitized = [self._sanitize_memory_dict(memory) for memory in raw_results]
        if not deserialize:
            return sanitized

        return [UserMemory.from_dict(memory) for memory in sanitized]


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
        return SafePostgresDb(
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
        print("✅ Database connected successfully")
        print(f"   URL: {db_config.database_url.split('@')[1]}")  # Hide password
        print("   Memory table: user_memories")
        print("   Session table: agent_sessions")
        print("   Run table: agent_runs")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

    print("=" * 60)
