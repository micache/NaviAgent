"""Database helper functions for chat sessions and messages."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from supabase import Client, create_client

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
AGENT_NAME = "receptionist"


def get_supabase_client() -> Client:
    """Get Supabase client instance."""
    url = supabase_url
    key = supabase_key

    if not url or not key:
        raise ValueError("Missing SUPABASE_URL and SUPABASE_KEY in environment")

    return create_client(url, key)


def create_chat_session(user_id: str, session_id: str, title: str = "New Chat") -> Dict[str, Any]:
    """Create a new chat session in the database.

    Args:
        user_id: User ID
        session_id: Session ID (UUID)
        title: Session title

    Returns:
        Created session data
    """
    supabase = get_supabase_client()

    data = {
        "id": session_id,
        "user_id": user_id,
        "title": title,
        "created_at": datetime.utcnow().isoformat(),
        "update_at": datetime.utcnow().isoformat(),
        "agent_name": AGENT_NAME,
    }

    response = supabase.table("chat_sessions").insert(data).execute()
    return response.data[0] if response.data else data


def save_chat_message(
    session_id: str,
    role: str,
    content: str,
) -> Dict[str, Any]:
    """Save a chat message to the database.

    Args:
        session_id: Session ID
        role: Message role (user/assistant)
        content: Message content

    Returns:
        Created message data
    """
    supabase = get_supabase_client()

    data = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "created_at": datetime.utcnow().isoformat(),
    }
    update_session_timestamp(session_id)
    print("Updating session timestamp for session:", session_id)
    response = supabase.table("chat_messages").insert(data).execute()
    return response.data[0] if response.data else data


def get_session_messages(session_id: str) -> List[Dict[str, Any]]:
    """Get all messages for a session.

    Args:
        session_id: Session ID

    Returns:
        List of messages
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("chat_messages")
        .select("*")
        .eq("session_id", session_id)
        .order("created_at")
        .execute()
    )

    return response.data if response.data else []


def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
    """Get all sessions for a user, ordered by last update time.

    Args:
        user_id: User ID

    Returns:
        List of sessions sorted by update_at (most recent first)
    """
    supabase = get_supabase_client()

    response = (
        supabase.table("chat_sessions")
        .select("*")
        .eq("user_id", user_id)
        .eq("agent_name", AGENT_NAME)
        .order("update_at", desc=True)
        .execute()
    )

    return response.data if response.data else []


def update_session_timestamp(session_id: str) -> None:
    """Update the last update timestamp of a session.

    Args:
        session_id: Session ID
    """
    supabase = get_supabase_client()

    supabase.table("chat_sessions").update({"update_at": datetime.utcnow().isoformat()}).eq(
        "id", session_id
    ).execute()
