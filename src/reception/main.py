"""FastAPI application for NaviAgent Receptionist service."""

from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from reception.receptionist_agent import ReceptionistAgent

# Initialize FastAPI app
app = FastAPI(
    title="NaviAgent Receptionist API",
    description="API for travel planning receptionist agent",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single agent instance
agent = ReceptionistAgent()


class ChatRequest(BaseModel):
    """Request model for chat messages."""

    message: str
    image_url: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat messages."""

    response: str
    state: str
    travel_data: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "NaviAgent Receptionist API",
        "version": "1.0.0",
        "endpoints": {
            "POST /chat": "Send a message to the agent",
            "POST /reset": "Reset the conversation",
            "GET /status": "Get current state and travel data",
        },
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent and get a response.

    Args:
        request: Chat request with message and optional image_url.

    Returns:
        Agent's response with state and travel data.
    """
    response = agent.process_message(request.message, request.image_url)

    return ChatResponse(
        response=response, state=agent.state.value, travel_data=agent.get_travel_data()
    )


@app.post("/reset")
async def reset_conversation():
    """Reset the conversation to start over.

    Returns:
        Greeting message and initial state.
    """
    agent.reset()
    greeting = agent.greet_customer()

    return {"message": greeting, "state": agent.state.value}


@app.get("/status")
async def get_status():
    """Get current conversation status and travel data.

    Returns:
        Current state and collected travel data.
    """
    return {"state": agent.state.value, "travel_data": agent.get_travel_data()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
