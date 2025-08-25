"""
WebSocket management for real-time communication
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # Store active connections by session_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
        # Store SSE subscribers per session (list of asyncio.Queue)
        self.sse_subscribers: Dict[str, List[asyncio.Queue]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a WebSocket connection
        
        Parameters:
            websocket (WebSocket): The FastAPI WebSocket instance to accept.
            session_id (str): The session identifier associated with this connection.
        """
        try:
            await websocket.accept()
            self.active_connections[session_id] = websocket
            self.connection_metadata[session_id] = {
                "connected_at": asyncio.get_event_loop().time(),
                "message_count": 0
            }
            
            logger.info(f"WebSocket connected for session: {session_id}")
            
            # Send welcome message
            await self.send_message(session_id, {
                "type": "connection",
                "status": "connected",
                "session_id": session_id
            })
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket for session {session_id}: {e}")
            raise
    
    def disconnect(self, session_id: str):
        """Disconnect a WebSocket
        
        Parameters:
            session_id (str): The session identifier to disconnect and cleanup.
        """
        try:
            if session_id in self.active_connections:
                del self.active_connections[session_id]
            if session_id in self.connection_metadata:
                del self.connection_metadata[session_id]
            
            logger.info(f"WebSocket disconnected for session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket for session {session_id}: {e}")
    
    async def send_message(self, session_id: str, message: Dict):
        """Send a message to a specific session over WebSocket and publish to SSE subscribers
        
        Parameters:
            session_id (str): The target session identifier.
            message (Dict): The JSON-serializable message to send/publish.
        """
        try:
            if session_id in self.active_connections:
                websocket = self.active_connections[session_id]
                await websocket.send_text(json.dumps(message))
                
                # Update metadata
                if session_id in self.connection_metadata:
                    self.connection_metadata[session_id]["message_count"] += 1
                
                logger.debug(f"Sent message to session {session_id}: {message.get('type', 'unknown')}")
            else:
                logger.warning(f"No active connection for session: {session_id}")
            
            # Always publish to SSE subscribers regardless of WebSocket status
            await self._publish_sse(session_id, message)
                
        except Exception as e:
            logger.error(f"Failed to send message to session {session_id}: {e}")
            # Remove broken connection
            self.disconnect(session_id)
    
    async def broadcast_message(self, message: Dict, exclude_sessions: List[str] = None):
        """Broadcast a message to all connected sessions and publish to SSE subscribers
        
        Parameters:
            message (Dict): The JSON-serializable message to broadcast.
            exclude_sessions (List[str], optional): Session IDs to exclude from broadcast.
        """
        exclude_sessions = exclude_sessions or []
        
        for session_id in list(self.active_connections.keys()):
            if session_id not in exclude_sessions:
                await self.send_message(session_id, message)
        
        # Also publish to any sessions that may only have SSE subscribers
        for session_id in list(self.sse_subscribers.keys()):
            if session_id not in (exclude_sessions or []):
                await self._publish_sse(session_id, message)
    
    async def handle_message(self, session_id: str, message: str):
        """Handle incoming WebSocket message
        
        Parameters:
            session_id (str): The session identifier from which the message was received.
            message (str): The raw JSON string received from the client.
        """
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            logger.debug(f"Received WebSocket message from {session_id}: {message_type}")
            
            # Handle different message types
            if message_type == "ping":
                await self.send_message(session_id, {"type": "pong"})
            
            elif message_type == "agent_request":
                # Forward to agent manager (will be implemented)
                await self.send_message(session_id, {
                    "type": "agent_response",
                    "status": "processing",
                    "request_id": data.get("request_id")
                })
            
            elif message_type == "browser_task":
                # Forward to browser automation service
                await self.send_message(session_id, {
                    "type": "browser_response",
                    "status": "processing",
                    "task_id": data.get("task_id")
                })
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.send_message(session_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from session {session_id}: {message}")
            await self.send_message(session_id, {
                "type": "error",
                "message": "Invalid JSON format"
            })
        except Exception as e:
            logger.error(f"Error handling message from session {session_id}: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "message": "Internal server error"
            })
    
    def get_connection_count(self) -> int:
        """Get the number of active WebSocket connections
        
        Returns:
            int: The count of active WebSocket connections.
        """
        return len(self.active_connections)
    
    def get_connection_info(self, session_id: str) -> Optional[Dict]:
        """Get connection information for a session
        
        Parameters:
            session_id (str): The session identifier to query.
        Returns:
            Optional[Dict]: Connection metadata if exists, otherwise None.
        """
        return self.connection_metadata.get(session_id)
    
    def list_active_sessions(self) -> List[str]:
        """List all active session IDs for WebSockets
        
        Returns:
            List[str]: A list of session identifiers currently connected via WebSocket.
        """
        return list(self.active_connections.keys())

    # ===== SSE support =====
    def subscribe(self, session_id: str) -> asyncio.Queue:
        """Subscribe an SSE listener for a given session.
        
        Creates an asyncio.Queue to push events for the session and registers it.
        
        Parameters:
            session_id (str): The session to subscribe to.
        Returns:
            asyncio.Queue: The queue from which the subscriber will consume messages.
        """
        queue: asyncio.Queue = asyncio.Queue()
        self.sse_subscribers.setdefault(session_id, []).append(queue)
        logger.info(f"SSE subscriber added for session: {session_id} (total: {len(self.sse_subscribers[session_id])})")
        return queue

    def unsubscribe(self, session_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe an SSE listener for a given session.
        
        Parameters:
            session_id (str): The session to unsubscribe from.
            queue (asyncio.Queue): The queue that was returned from subscribe().
        """
        try:
            if session_id in self.sse_subscribers:
                subscribers = self.sse_subscribers[session_id]
                if queue in subscribers:
                    subscribers.remove(queue)
                    logger.info(f"SSE subscriber removed for session: {session_id} (remaining: {len(subscribers)})")
                if not subscribers:
                    del self.sse_subscribers[session_id]
        except Exception as e:
            logger.error(f"Error unsubscribing SSE for session {session_id}: {e}")

    async def _publish_sse(self, session_id: str, message: Dict) -> None:
        """Publish a message to all SSE subscribers for the given session.
        
        Parameters:
            session_id (str): The target session identifier.
            message (Dict): The message to publish to subscribers.
        """
        try:
            if session_id not in self.sse_subscribers:
                return
            for queue in list(self.sse_subscribers.get(session_id, [])):
                try:
                    await queue.put(message)
                except Exception as e:
                    logger.error(f"Failed to put message into SSE queue for session {session_id}: {e}")
        except Exception as e:
            logger.error(f"Error publishing SSE for session {session_id}: {e}")
