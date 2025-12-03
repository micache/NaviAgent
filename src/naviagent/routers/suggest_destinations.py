"""API endpoints for destination suggestions."""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from reception.suggestion_agent import get_suggestion_from_text

from ..core.auth import authenticate_user
from ..models.models import ChatMessage as ChatMessageModel
from ..models.models import ChatSession as ChatSessionModel

router = APIRouter(prefix="/destinations", tags=["destinations"])


class DestinationRequest(BaseModel):
    """Request model for destination suggestion."""

    description: str


class DestinationResponse(BaseModel):
    """Response model for destination suggestion."""

    session_id: str
    destination: str
    reason: str


@router.post("/suggest", response_model=DestinationResponse)
async def suggest_destination(
    request: DestinationRequest, auth: Dict[str, Any] = Depends(authenticate_user)
):
    """
    Suggest a travel destination based on user description.
    Creates a new chat session and stores the conversation.

    Args:
        request: DestinationRequest containing the description
        auth: Authenticated user info

    Returns:
        DestinationResponse with session_id, suggested destination and reason
    """
    try:
        user_id = auth["user_id"]
        supabase = auth["supabase"]

        # Create session first to pass to agent
        session_data = {
            ChatSessionModel.user_id.key: user_id,
            ChatSessionModel.title.key: f"Destination suggestion",
            ChatSessionModel.created_at.key: datetime.utcnow().isoformat(),
            ChatSessionModel.update_at.key: datetime.utcnow().isoformat(),
        }
        session_res = (
            supabase.table(ChatSessionModel.__tablename__).insert(session_data).execute()
        )
        session_row = getattr(session_res, "data", [{}])[0]
        session_id = session_row.get(ChatSessionModel.id.key)

        if not session_id:
            raise HTTPException(status_code=500, detail="Failed to create chat session")

        # Store user message
        user_msg = {
            ChatMessageModel.session_id.key: session_id,
            ChatMessageModel.role.key: "user",
            ChatMessageModel.content.key: request.description,
            ChatMessageModel.created_at.key: datetime.utcnow().isoformat(),
        }
        supabase.table(ChatMessageModel.__tablename__).insert(user_msg).execute()

        # Get suggestion from agent (returns markdown text)
        result = get_suggestion_from_text(
            description=request.description,
            user_id=user_id,
            session_id=session_id
        )
        
        print(f"DEBUG - Agent result: {result}")  # Debug log

        # Extract first destination for session title only
        lines = result.strip().split('\n')
        first_dest_line = lines[0] if lines else "Destinations"
        destination = first_dest_line.replace('🌍', '').strip('*').strip()

        # Update session title with first destination
        update_data = {
            ChatSessionModel.title.key: f"Destination: {destination}",
            ChatSessionModel.update_at.key: datetime.utcnow().isoformat(),
        }
        supabase.table(ChatSessionModel.__tablename__).update(update_data).eq(
            ChatSessionModel.id.key, session_id
        ).execute()

        # Store assistant response (full markdown)
        assistant_msg = {
            ChatMessageModel.session_id.key: session_id,
            ChatMessageModel.role.key: "assistant",
            ChatMessageModel.content.key: result,
            ChatMessageModel.created_at.key: datetime.utcnow().isoformat(),
        }
        supabase.table(ChatMessageModel.__tablename__).insert(assistant_msg).execute()

        return DestinationResponse(
            session_id=session_id, destination=destination, reason=result
        )
    except Exception as e:
        import traceback
        print(f"ERROR in suggest_destination: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Error getting destination suggestion: {str(e)}"
        ) from e
