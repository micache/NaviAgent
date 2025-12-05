"""FastAPI application for NaviAgent Receptionist service."""

import json
import uuid
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from reception.db_helpers import (
    create_chat_session,
    get_session_messages,
    get_user_sessions,
    save_chat_message,
    update_session_timestamp,
)
from reception.receptionist_agent import ReceptionistAgent

# Initialize FastAPI app
app = FastAPI(
    title="NaviAgent Receptionist API",
    description="API for travel planning receptionist agent",
    version="2.0.0",
)

# In-memory cache for agent instances
_agent_cache: Dict[str, ReceptionistAgent] = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartChatRequest(BaseModel):
    """Request model for starting a new chat session."""

    user_id: str


class StartChatResponse(BaseModel):
    """Response model for starting a new chat session."""

    session_id: str
    message: str


class ChatRequest(BaseModel):
    """Request model for chat messages."""

    session_id: str
    message: str


class ChatResponse(BaseModel):
    """Response model for chat messages."""

    message: str
    travel_data: Dict[str, Any]
    is_complete: bool = False


class SessionInfo(BaseModel):
    """Session information model."""

    session_id: str
    user_id: str
    created_at: Optional[str] = None


class MessageInfo(BaseModel):
    """Message information model."""

    id: str
    session_id: str
    role: str
    content: str
    created_at: str


class SessionListResponse(BaseModel):
    """Response model for session list."""

    sessions: List[Dict[str, Any]]


class MessageListResponse(BaseModel):
    """Response model for message list."""

    messages: List[Dict[str, Any]]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "NaviAgent Receptionist API",
        "version": "2.0.0",
        "endpoints": {
            "POST /start_chat": "Start a new chat session",
            "POST /chat": "Send a message in an existing session",
            "GET /sessions/{user_id}": "Get all sessions for a user",
            "GET /sessions/{session_id}/messages": "Get chat history for a session",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import os
    checks = {
        "status": "ok",
        "supabase_url": bool(os.getenv("SUPABASE_URL")),
        "supabase_key": bool(os.getenv("SUPABASE_KEY")),
        "openai_api_key": bool(os.getenv("OPENAI_API_KEY")),
        "database_url": bool(os.getenv("DATABASE_URL")),
    }
    return checks


@app.post("/start_chat", response_model=StartChatResponse)
async def start_chat(request: StartChatRequest):
    """Start a new chat session.

    Args:
        request: Request with user_id.

    Returns:
        New session_id and greeting message.
    """
    try:
        print("\n" + "="*80)
        print("🆕 START_CHAT endpoint called")
        print(f"👤 User ID: {request.user_id}")
        
        # Generate new session_id
        session_id = str(uuid.uuid4())
        print(f"🆔 Generated session_id: {session_id}")

        # Create session in database
        print("💾 Creating session in database...")
        create_chat_session(
            user_id=request.user_id, session_id=session_id, title="Travel Planning Session"
        )
        print("✅ Session created in database")

        # Create agent and cache it
        print("🤖 Initializing ReceptionistAgent...")
        agent = ReceptionistAgent(
            user_id=request.user_id,
            session_id=session_id,
        )
        _agent_cache[session_id] = agent
        print("✅ Agent initialized and cached")

        # Get greeting
        print("💬 Getting greeting from agent...")
        greeting = agent.greet_customer()
        print(f"✅ Greeting: {greeting[:100]}...")

        # Save greeting message
        print("💾 Saving greeting message...")
        save_chat_message(
            session_id=session_id,
            role="assistant",
            content=greeting,
        )
        print("✅ Greeting saved")
        print("="*80 + "\n")

        return StartChatResponse(
            session_id=session_id,
            message=greeting,
        )
    except Exception as e:
        print("\n" + "❌"*40)
        print(f"ERROR in start_chat: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback:\n{traceback.format_exc()}")
        print("❌"*40 + "\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message in an existing session.

    Args:
        request: Chat request with session_id and message.

    Returns:
        Agent's response and current travel data.
    """
    try:
        # Save user message to database
        save_chat_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
        )

        # Get or create agent from cache
        if request.session_id not in _agent_cache:
            agent = ReceptionistAgent(
                session_id=request.session_id,
            )
            _agent_cache[request.session_id] = agent
        else:
            agent = _agent_cache[request.session_id]

        # Process message
        response = agent.run(request.message)

        # Save assistant response to database
        save_chat_message(
            session_id=request.session_id,
            role="assistant",
            content=response.content,
        )

        # Update session timestamp
        update_session_timestamp(request.session_id)

        # Check if conversation is complete
        travel_data = agent.get_travel_data()
        is_complete = False

        # Print travel data for debugging
        print("\n" + "="*80)
        print("📋 TRAVEL DATA COLLECTED:")
        print(json.dumps(travel_data, indent=2, ensure_ascii=False))
        print("="*80 + "\n")

        # Check if all required fields are filled
        required_fields = [
            "destination",
            "departure_point",
            "departure_date",
            "trip_duration",
            "num_travelers",
            "budget",
            "travel_style",
        ]
        
        # Count filled fields
        filled_fields = sum(1 for field in required_fields if travel_data.get(field) is not None)
        print(f"✅ Filled fields: {filled_fields}/{len(required_fields)}")
        print(f"📝 Missing fields: {[f for f in required_fields if travel_data.get(f) is None]}")
        print("-"*80 + "\n")
        if all(travel_data.get(field) is not None for field in required_fields):
            # Use LLM to detect if customer confirmed (handles nuanced responses)
            confirmation_prompt = (
                f"Phân tích câu trả lời của khách hàng: '{request.message}'\n\n"
                f"Context: Nhân viên vừa hỏi 'Bạn có xác nhận thông tin này không?'\n\n"
                f"Hãy phân tích xem khách hàng có đang XÁC NHẬN (agree/confirm) hay KHÔNG XÁC NHẬN (disagree/reject)?\n\n"
                f"Ví dụ:\n"
                f"- 'ok' → XÁC NHẬN\n"
                f"- 'đúng rồi' → XÁC NHẬN\n"
                f"- 'chưa đúng' → KHÔNG XÁC NHẬN\n"
                f"- 'sai rồi' → KHÔNG XÁC NHẬN\n"
                f"- 'có' (trong ngữ cảnh này) → XÁC NHẬN\n"
                f"- 'không' → KHÔNG XÁC NHẬN\n\n"
                f"Trả về CHỈ MỘT từ: 'YES' hoặc 'NO'"
            )

            try:
                check_response = agent.run(confirmation_prompt)
                is_confirmed = "YES" in check_response.content.upper()
                is_complete = is_confirmed
                
                if is_complete:
                    print("\n" + "🎉"*40)
                    print("✅ TRAVEL DATA COLLECTION COMPLETE!")
                    print("📦 FINAL TRAVEL DATA FOR BACKEND:")
                    print(json.dumps(travel_data, indent=2, ensure_ascii=False))
                    print("🎉"*40 + "\n")
            except Exception:
                # Fallback to simple keyword check if LLM fails
                positive_keywords = ["ok", "có", "đúng", "xác nhận", "yes", "vâng", "ừ", "oke"]
                is_complete = any(
                    keyword in request.message.lower() for keyword in positive_keywords
                )
                
                if is_complete:
                    print("\n" + "🎉"*40)
                    print("✅ TRAVEL DATA COLLECTION COMPLETE! (Fallback detection)")
                    print("📦 FINAL TRAVEL DATA FOR BACKEND:")
                    print(json.dumps(travel_data, indent=2, ensure_ascii=False))
                    print("🎉"*40 + "\n")

        return ChatResponse(
            message=response.content,
            travel_data=travel_data,
            is_complete=is_complete,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{user_id}", response_model=SessionListResponse)
async def get_sessions(user_id: str):
    """Get all chat sessions for a user.

    Args:
        user_id: User ID

    Returns:
        List of sessions
    """
    try:
        sessions = get_user_sessions(user_id)
        return SessionListResponse(sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sessions/{session_id}/messages", response_model=MessageListResponse)
async def get_messages(session_id: str):
    """Get all messages for a session.

    Args:
        session_id: Session ID

    Returns:
        List of messages
    """
    try:
        messages = get_session_messages(session_id)
        return MessageListResponse(messages=messages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
