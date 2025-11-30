"""FastAPI application for NaviAgent Receptionist service."""

import uuid
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from reception.receptionist_agent import ReceptionistAgent

# Initialize FastAPI app
app = FastAPI(
    title="NaviAgent Receptionist API",
    description="API for travel planning receptionist agent",
    version="2.0.0",
)

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


class SessionInfo(BaseModel):
    """Session information model."""

    session_id: str
    user_id: str
    created_at: Optional[str] = None


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


@app.post("/start_chat", response_model=StartChatResponse)
async def start_chat(request: StartChatRequest):
    """Start a new chat session.

    Args:
        request: Request with user_id.

    Returns:
        New session_id and greeting message.
    """
    try:
        # Generate new session_id
        session_id = str(uuid.uuid4())

        # Create agent with storage
        agent = ReceptionistAgent(
            user_id=request.user_id,
            session_id=session_id,
        )

        # Get greeting
        greeting = agent.greet_customer()

        return StartChatResponse(
            session_id=session_id,
            message=greeting,
        )
    except Exception as e:
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
        # Create agent with existing session
        agent = ReceptionistAgent(
            session_id=request.session_id,
        )

        # Process message
        response = agent.run(request.message)

        return ChatResponse(
            message=response.content,
            travel_data=agent.get_travel_data(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
