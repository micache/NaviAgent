import json
import sys
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import uuid
from reception.config import settings
from reception.receptionist_agent import ReceptionistAgent
import requests
import time
import sys
from pathlib import Path

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Receptionist Agent of NaviAgent.
    
    ## Features
    - Suggest travel destinations based on user text descriptions.
    - Analyze images to identify landmarks and locations.
    - Collect metadata of trip during conversation.
    """,
    docs_url=f"{settings.api_prefix}/docs",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    redoc_url=f"{settings.api_prefix}/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods,
    allow_headers=settings.allow_headers,
)

# Store active sessions in memory
sessions: Dict[str, ReceptionistAgent] = {}


@app.get(f"{settings.api_prefix}/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post(f"{settings.api_prefix}/session/start")
async def start_session():
    """Start a new conversation session with the receptionist agent."""
    try:
        session_id = str(uuid.uuid4())
        agent = ReceptionistAgent()
        
        # Get greeting message
        greeting = agent.greet()
        
        # Store session
        sessions[session_id] = agent
        
        return {
            "session_id": session_id,
            "message": greeting
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@app.post(f"{settings.api_prefix}/chat")
async def chat(request: Request):
    """Send a message to the agent and get a response."""
    body = await request.json()
    session_id = body.get("session_id")
    message = body.get("message")
    
    if not session_id or not message:
        raise HTTPException(status_code=400, detail="session_id and message are required")
    
    # Check if session exists
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please start a new session.")
    
    try:
        agent = sessions[session_id]
        
        # Process message
        agent_response = agent.chat(message)
        
        # Get current metadata
        metadata = agent.get_metadata_summary()
        
        return {
            "session_id": session_id,
            "agent_message": agent_response,
            "metadata": metadata,
            "is_complete": agent.is_information_complete(),
            "is_confirmed": agent.information_confirmed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.get(f"{settings.api_prefix}/session/{{session_id}}/metadata")
async def get_metadata(session_id: str):
    """Get collected metadata for a session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        agent = sessions[session_id]
        
        return {
            "session_id": session_id,
            "metadata": agent.get_metadata_summary(),
            "is_complete": agent.is_information_complete()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")


@app.delete(f"{settings.api_prefix}/session/{{session_id}}")
async def end_session(session_id: str):
    """End a conversation session and clean up."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get final metadata before deleting
        agent = sessions[session_id]
        final_metadata = agent.get_metadata_summary()
        
        # Clean up session
        del sessions[session_id]
        
        return {
            "message": "Session ended successfully",
            "session_id": session_id,
            "final_metadata": final_metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


@app.get(f"{settings.api_prefix}/sessions/count")
async def get_active_sessions():
    """Get count of active sessions."""
    return {
        "active_sessions": len(sessions),
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get(f"{settings.api_prefix}/sessions/list")
async def list_sessions():
    """List all active session IDs."""
    return {
        "sessions": list(sessions.keys()),
        "count": len(sessions)
    }

def run():
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.reload
    )
    
def main():
    """Test the API with a sample conversation flow"""
    
    # Use localhost for testing instead of 0.0.0.0
    test_host = "localhost" if settings.host == "0.0.0.0" else settings.host
    BASE_URL = f"http://{test_host}:{settings.port}{settings.api_prefix}"
    
    print("="*80)
    print("Testing NaviAgent Reception API")
    print(f"Target: {BASE_URL}")
    print("="*80)
    
    try:
        # 1. Start session
        print("\n1. Starting session...")
        response = requests.post(f"{BASE_URL}/session/start")
        data = response.json()
        session_id = data["session_id"]
        print(f"   Session ID: {session_id}")
        print(f"   Greeting: {data['message']}")
        
        # 2. Chat - Send messages
        messages = [
            "Hanoi, Vietnam",
            "Seoul",
            "5 days",
            "2 people",
            "20 million VND",
            "Food and shopping",
            "No special requirements"
        ]
        
        for i, msg in enumerate(messages, 1):
            print(f"\n{i+1}. Sending message: '{msg}'")
            response = requests.post(f"{BASE_URL}/chat", json={
                "session_id": session_id,
                "message": msg
            })
            data = response.json()
            print(f"   Agent: {data['agent_message']}")
            print(f"   Complete: {data['is_complete']}")
            time.sleep(1)
        
        # 3. Get metadata and save to file
        print("\n3. Getting final metadata...")
        response = requests.get(f"{BASE_URL}/session/{session_id}/metadata")
        data = response.json()
        metadata = data['metadata']
        
        # Print to console
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
        
        # Save to file in same directory as main.py
        # output_dir = Path(__file__).resolve().parent / "sessions"
        # output_dir.mkdir(parents=True, exist_ok=True)
        
        # timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # filename = f"session_{session_id[:8]}_{timestamp}.json"
        # filepath = output_dir / filename
        
        # with open(filepath, "w", encoding="utf-8") as f:
        #     json.dump({
        #         "session_id": session_id,
        #         "timestamp": datetime.utcnow().isoformat(),
        #         "metadata": metadata
        #     }, f, indent=2, ensure_ascii=False)
        
        # print(f"\n   Saved to: {filepath}")
        
        # 4. End session
        print("\n4. Ending session...")
        response = requests.delete(f"{BASE_URL}/session/{session_id}")
        print(f"   {response.json()['message']}")
        
        print("\n" + "="*80)
        print("Test completed successfully!")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to API server.")
        print(f"Make sure server is running at: http://{test_host}:{settings.port}")
        print("\nTo start server:")
        print("  python -m reception.main")
    except Exception as e:
        print(f"\nError: {e}")
    
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run test mode
        main()
    else:
        # Run server mode
        run()
