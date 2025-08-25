"""
Session management for AI Agent System
Handles user sessions, conversation history, and state persistence
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import aioredis
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SessionData(BaseModel):
    """Session data model"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime
    last_activity: datetime
    conversation_history: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    agent_state: Dict[str, Any] = {}


class SessionManager:
    """Manages user sessions and conversation state"""
    
    def __init__(self, redis_url: str, mongodb_url: str):
        self.redis_url = redis_url
        self.mongodb_url = mongodb_url
        self.redis: Optional[aioredis.Redis] = None
        self.mongodb: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def initialize(self):
        """Initialize Redis and MongoDB connections"""
        try:
            # Initialize Redis
            self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("Redis connection established")
            
            # Initialize MongoDB
            self.mongodb = AsyncIOMotorClient(self.mongodb_url)
            self.db = self.mongodb.agent_system
            
            # Test MongoDB connection
            await self.db.command("ping")
            logger.info("MongoDB connection established")
            
            # Create indexes
            await self._create_indexes()
            
        except Exception as e:
            logger.error(f"Failed to initialize session manager: {e}")
            raise
    
    async def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Create indexes on sessions collection
            await self.db.sessions.create_index("session_id", unique=True)
            await self.db.sessions.create_index("user_id")
            await self.db.sessions.create_index("last_activity")
            
            logger.info("Database indexes created")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            last_activity=now
        )
        
        try:
            # Store in MongoDB for persistence
            await self.db.sessions.insert_one(session_data.dict())
            
            # Cache in Redis for fast access
            await self.redis.setex(
                f"session:{session_id}",
                3600,  # 1 hour TTL
                json.dumps(session_data.dict(), default=str)
            )
            
            logger.info(f"Created session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data"""
        try:
            # Try Redis first
            cached_data = await self.redis.get(f"session:{session_id}")
            if cached_data:
                data = json.loads(cached_data)
                return SessionData(**data)
            
            # Fallback to MongoDB
            doc = await self.db.sessions.find_one({"session_id": session_id})
            if doc:
                session_data = SessionData(**doc)
                
                # Update Redis cache
                await self.redis.setex(
                    f"session:{session_id}",
                    3600,
                    json.dumps(session_data.dict(), default=str)
                )
                
                return session_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session data"""
        try:
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            # Update last activity
            updates["last_activity"] = datetime.utcnow()
            
            # Update MongoDB
            await self.db.sessions.update_one(
                {"session_id": session_id},
                {"$set": updates}
            )
            
            # Update Redis cache
            for key, value in updates.items():
                setattr(session, key, value)
            
            await self.redis.setex(
                f"session:{session_id}",
                3600,
                json.dumps(session.dict(), default=str)
            )
            
            logger.debug(f"Updated session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            raise
    
    async def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        try:
            session = await self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found")
            
            session.conversation_history.append(message)
            
            await self.update_session(session_id, {
                "conversation_history": session.conversation_history
            })
            
        except Exception as e:
            logger.error(f"Failed to add message to session {session_id}: {e}")
            raise
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history for a session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return []
            
            # Return last N messages
            return session.conversation_history[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get conversation history for {session_id}: {e}")
            return []
    
    async def delete_session(self, session_id: str):
        """Delete a session"""
        try:
            # Remove from Redis
            await self.redis.delete(f"session:{session_id}")
            
            # Remove from MongoDB
            await self.db.sessions.delete_one({"session_id": session_id})
            
            logger.info(f"Deleted session: {session_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise
    
    async def cleanup_expired_sessions(self, max_age_hours: int = 24):
        """Clean up expired sessions"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Find expired sessions
            expired_sessions = await self.db.sessions.find(
                {"last_activity": {"$lt": cutoff_time}}
            ).to_list(length=None)
            
            # Delete expired sessions
            for session in expired_sessions:
                await self.delete_session(session["session_id"])
            
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.redis:
                await self.redis.close()
            if self.mongodb:
                self.mongodb.close()
            logger.info("Session manager cleanup complete")
        except Exception as e:
            logger.error(f"Error during session manager cleanup: {e}")
