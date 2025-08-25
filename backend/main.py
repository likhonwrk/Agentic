"""
AI Agent System - FastAPI Backend
Powerful AI agent system with browser automation, MCP integration, and multi-modal capabilities
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.agent_manager import AgentManager
from core.browser_automation import BrowserAutomationService
from core.mcp_integration import MCPServerManager
from core.session_manager import SessionManager
from core.websocket_manager import WebSocketManager
from utils.config import Settings
from utils.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global managers
agent_manager: Optional[AgentManager] = None
browser_service: Optional[BrowserAutomationService] = None
mcp_manager: Optional[MCPServerManager] = None
session_manager: Optional[SessionManager] = None
websocket_manager: Optional[WebSocketManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent_manager, browser_service, mcp_manager, session_manager, websocket_manager
    
    logger.info("Starting AI Agent System...")
    
    # Initialize core services
    settings = Settings()
    
    # Initialize session manager
    session_manager = SessionManager(
        redis_url=settings.redis_url,
        mongodb_url=settings.mongodb_url
    )
    await session_manager.initialize()
    
    # Initialize browser automation service
    browser_service = BrowserAutomationService()
    await browser_service.initialize()
    
    # Initialize MCP server manager
    mcp_manager = MCPServerManager()
    await mcp_manager.initialize()
    
    # Initialize WebSocket manager
    websocket_manager = WebSocketManager()
    
    # Initialize agent manager
    agent_manager = AgentManager(
        session_manager=session_manager,
        browser_service=browser_service,
        mcp_manager=mcp_manager,
        websocket_manager=websocket_manager
    )
    await agent_manager.initialize()
    
    logger.info("AI Agent System started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down AI Agent System...")
    if agent_manager:
        await agent_manager.cleanup()
    if browser_service:
        await browser_service.cleanup()
    if mcp_manager:
        await mcp_manager.cleanup()
    if session_manager:
        await session_manager.cleanup()
    
    logger.info("AI Agent System shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="AI Agent System",
    description="Powerful AI agent system with browser automation and MCP integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AgentRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    agent_type: str = "default"
    tools: List[str] = []
    context: Dict = {}

class AgentResponse(BaseModel):
    response: str
    session_id: str
    agent_id: str
    metadata: Dict = {}

class BrowserTask(BaseModel):
    action: str
    url: Optional[str] = None
    selector: Optional[str] = None
    text: Optional[str] = None
    options: Dict = {}

# API Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "AI Agent System is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "services": {
            "agent_manager": agent_manager is not None,
            "browser_service": browser_service is not None,
            "mcp_manager": mcp_manager is not None,
            "session_manager": session_manager is not None,
        }
    }
    return health_status

@app.post("/agent/chat", response_model=AgentResponse)
async def chat_with_agent(request: AgentRequest):
    """Chat with an AI agent"""
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not initialized")
    
    try:
        response = await agent_manager.process_message(
            message=request.message,
            session_id=request.session_id,
            agent_type=request.agent_type,
            tools=request.tools,
            context=request.context
        )
        return response
    except Exception as e:
        logger.error(f"Error processing agent request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/browser/execute")
async def execute_browser_task(task: BrowserTask):
    """Execute browser automation task"""
    if not browser_service:
        raise HTTPException(status_code=503, detail="Browser service not initialized")
    
    try:
        result = await browser_service.execute_task(
            action=task.action,
            url=task.url,
            selector=task.selector,
            text=task.text,
            options=task.options
        )
        return {"result": result, "status": "success"}
    except Exception as e:
        logger.error(f"Error executing browser task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if not session_manager:
        raise HTTPException(status_code=503, detail="Session manager not initialized")
    
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        logger.error(f"Error retrieving session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    if not mcp_manager:
        raise HTTPException(status_code=503, detail="MCP manager not initialized")
    
    try:
        tools = await mcp_manager.list_tools()
        return {"tools": tools}
    except Exception as e:
        logger.error(f"Error listing MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time communication
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time agent communication"""
    if not websocket_manager:
        await websocket.close(code=1011, reason="WebSocket manager not initialized")
        return
    
    await websocket_manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(session_id, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason="Internal error")

# Mount static files (for serving the Next.js frontend if needed)
if os.path.exists("/app/frontend"):
    app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
