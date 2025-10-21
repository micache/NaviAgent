from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_current_user
from ..core.database import get_supabase_authed
from ..models.models import ChatMessage as ChatMessageModel, ChatSession as ChatSessionModel
from ..schemas.models import ChatMessage, ChatSession


router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=List[ChatSession])
def list_sessions(current_user: Dict[str, Any] = Depends(get_current_user)) -> List[ChatSession]:
    token = current_user.get("_access_token")
    supabase = get_supabase_authed(token)
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user in token")

    res = (
        supabase.table(ChatSessionModel.__tablename__)
        .select("*")
        .eq(ChatSessionModel.user_id.key, user_id)
        .order(ChatSessionModel.update_at.key, desc=True)
        .execute()
    )
    rows = getattr(res, "data", []) or []
    return [ChatSession(**row) for row in rows]


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
def list_messages(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[ChatMessage]:
    token = current_user.get("_access_token")
    supabase = get_supabase_authed(token)
    user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(current_user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user in token")

    # Verify the session belongs to the user
    sess_query = supabase.table(ChatSessionModel.__tablename__).select(f"{ChatSessionModel.id.key},{ChatSessionModel.user_id.key}").eq(ChatSessionModel.id.key, session_id)
    if hasattr(sess_query, "maybe_single"):
        sess = sess_query.maybe_single().execute()
        sess_row = getattr(sess, "data", None)
    else:
        sess = sess_query.execute()
        sess_data = getattr(sess, "data", None)
        sess_row = sess_data[0] if isinstance(sess_data, list) and sess_data else None
    if not sess_row or sess_row.get(ChatSessionModel.user_id.key) != user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    res = (
        supabase.table(ChatMessageModel.__tablename__)
        .select("*")
        .eq(ChatMessageModel.session_id.key, session_id)
        .order(ChatMessageModel.created_at.key, desc=False)
        .execute()
    )
    rows = getattr(res, "data", []) or []
    return [ChatMessage(**row) for row in rows]
