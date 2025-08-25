"""
Mock server for Agentic AI Agent System testing
Provides mock endpoints for development and testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import uvicorn
import json
import time
from datetime import datetime

app = FastAPI(
    title="Agentic Mock Server",
    description="Mock server for testing Agentic AI Agent System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data storage
mock_sessions: Dict[str, Dict] = {}
mock_agents: List[Dict] = [
    {
        "id": "agent-1",
        "name": "WebCrawler",
        "type": "browser",
        "status": "active",
        "created_at": "2025-01-27T10:00:00Z"
    },
    {
        "id": "agent-2", 
        "name": "DataProcessor",
        "type": "data",
        "status": "idle",
        "created_at": "2025-01-27T09:30:00Z"
    }
]

class SessionCreate(BaseModel):
    title: str = "New Session"
    agent_type: str = "chat"

class MessageCreate(BaseModel):
    content: str
    type: str = "user"

@app.get("/")
async def root():
    return {"message": "Agentic Mock Server", "version": "1.0.0"}

@app.get("/api/v1/sessions")
async def list_sessions():
    """List all sessions"""
    return {"sessions": list(mock_sessions.values())}

@app.post("/api/v1/sessions")
async def create_session(session: SessionCreate):
    """Create a new session"""
    session_id = f"session-{int(time.time())}"
    new_session = {
        "id": session_id,
        "title": session.title,
        "agent_type": session.agent_type,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }
    mock_sessions[session_id] = new_session
    return new_session

@app.get("/api/v1/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    if session_id not in mock_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return mock_sessions[session_id]

@app.post("/api/v1/sessions/{session_id}/chat")
async def send_message(session_id: str, message: MessageCreate):
    """Send message to session"""
    if session_id not in mock_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Add user message
    user_msg = {
        "id": f"msg-{int(time.time())}",
        "content": message.content,
        "type": "user",
        "timestamp": datetime.now().isoformat()
    }
    mock_sessions[session_id]["messages"].append(user_msg)
    
    # Simulate agent response
    agent_msg = {
        "id": f"msg-{int(time.time()) + 1}",
        "content": f"Mock response to: {message.content}",
        "type": "agent",
        "timestamp": datetime.now().isoformat(),
        "agent_name": "MockAgent"
    }
    mock_sessions[session_id]["messages"].append(agent_msg)
    
    return {"status": "success", "message": "Message sent"}

@app.get("/api/v1/agents")
async def list_agents():
    """List all agents"""
    return {"agents": mock_agents}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
