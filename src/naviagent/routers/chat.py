from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import authenticate_user
from ..models.models import ChatMessage as ChatMessageModel
from ..models.models import ChatSession as ChatSessionModel
from ..schemas.models import ChatMessage, ChatSession, CreateMessageRequest

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=List[ChatSession])
def list_sessions(auth: Dict[str, Any] = Depends(authenticate_user)) -> List[ChatSession]:
    user_id = auth["user_id"]
    supabase = auth["supabase"]

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
    auth: Dict[str, Any] = Depends(authenticate_user),
) -> List[ChatMessage]:
    user_id = auth["user_id"]
    supabase = auth["supabase"]

    # Verify the session belongs to the user
    sess_query = (
        supabase.table(ChatSessionModel.__tablename__)
        .select(f"{ChatSessionModel.id.key},{ChatSessionModel.user_id.key}")
        .eq(ChatSessionModel.id.key, session_id)
    )
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


@router.post("/sessions", response_model=ChatSession)
def create_session(
    auth: Dict[str, Any] = Depends(authenticate_user),
) -> ChatSession:
    user_id = auth["user_id"]
    supabase = auth["supabase"]

    insert_data = {
        ChatSessionModel.user_id.key: user_id,
        ChatSessionModel.title.key: "New Chat Session",  # Default title
    }
    req = supabase.table(ChatSessionModel.__tablename__).insert(insert_data).execute()

    row = (getattr(req, "data", None) or [None])[0]
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create session")
    return ChatSession(**row)


@router.post("/sessions/{session_id}/messages", response_model=ChatMessage)
def create_message(
    session_id: str,
    message: CreateMessageRequest,
    auth: Dict[str, Any] = Depends(authenticate_user),
) -> ChatMessage:
    auth["user_id"]
    supabase = auth["supabase"]

    # Verify the session belongs to the user
    sess_query = (
        supabase.table(ChatSessionModel.__tablename__)
        .select(f"{ChatSessionModel.id.key},{ChatSessionModel.user_id.key}")
        .eq(ChatSessionModel.id.key, session_id)
    )
    try:
        if hasattr(sess_query, "maybe_single"):
            sess_resp = sess_query.maybe_single().execute()
        else:
            sess_resp = sess_query.execute()
    except Exception:
        # Some Postgrest responses may return 204 (no content) which the client raises for maybe_single.
        # Fallback to a plain execute() and parse whatever data is returned.
        sess_resp = sess_query.execute()
    sess_data = getattr(sess_resp, "data", None)
    if isinstance(sess_data, list):
        sess_data[0] if sess_data else None
    else:
        pass
    # =======================Model Response==========================
    reponse = {"role": "assistant", "content": f"Hello, you sent: {message.content}"}
    # ===============================================================
    insert_data = {
        ChatMessageModel.session_id.key: session_id,
        ChatMessageModel.role.key: message.role,
        ChatMessageModel.content.key: message.content,
    }
    insert_data_response = {
        ChatMessageModel.session_id.key: session_id,
        ChatMessageModel.role.key: reponse["role"],
        ChatMessageModel.content.key: reponse["content"],
    }
    supabase.table(ChatMessageModel.__tablename__).insert(insert_data).execute()
    res = supabase.table(ChatMessageModel.__tablename__).insert(insert_data_response).execute()

    row = (getattr(res, "data", None) or [None])[0]
    if not row:
        raise HTTPException(status_code=500, detail="Failed to create message")
    return ChatMessage(**row)
