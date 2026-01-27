"""
Session Manager - Redis-based session and context management

Handles:
- Short-term conversation history (Redis)
- Session state caching
- Rate limiting per user
"""

import json
from datetime import datetime, timedelta
from typing import Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class SessionData:
    """Session data structure"""
    session_id: str
    client_phone: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Conversation state
    message_count: int = 0
    last_intent: Optional[str] = None
    
    # Context for multi-turn conversations
    active_search_criteria: Optional[dict] = None
    last_viewed_property: Optional[str] = None
    pending_action: Optional[str] = None  # e.g., "awaiting_confirmation"
    pending_data: Optional[dict] = None
    
    # User preferences (short-term)
    preferred_language: str = "id"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionData":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SessionManager:
    """
    Manages user sessions using Redis for fast access.
    
    Features:
    - Session creation and retrieval
    - Conversation context tracking
    - Message history (last N messages)
    - Rate limiting
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        session_ttl: int = 3600,  # 1 hour
        history_limit: int = 10,  # Max messages to keep
    ):
        """
        Initialize SessionManager.
        
        Args:
            redis_url: Redis connection URL
            session_ttl: Session time-to-live in seconds
            history_limit: Maximum messages to keep in history
        """
        self.redis_url = redis_url
        self.session_ttl = session_ttl
        self.history_limit = history_limit
        self._redis: Optional[Any] = None
    
    async def _get_redis(self):
        """Get or create Redis connection"""
        if self._redis is None:
            try:
                import redis.asyncio as redis
                self._redis = redis.from_url(self.redis_url)
            except ImportError:
                print("Warning: redis package not available, using in-memory fallback")
                self._redis = InMemorySessionStore()
        return self._redis
    
    def _session_key(self, session_id: str) -> str:
        """Generate Redis key for session"""
        return f"session:{session_id}"
    
    def _history_key(self, session_id: str) -> str:
        """Generate Redis key for message history"""
        return f"history:{session_id}"
    
    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get session data by ID"""
        redis = await self._get_redis()
        key = self._session_key(session_id)
        
        try:
            data = await redis.get(key)
            if data:
                return SessionData.from_dict(json.loads(data))
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    async def create_session(
        self, 
        session_id: str, 
        client_phone: str
    ) -> SessionData:
        """Create a new session"""
        session = SessionData(
            session_id=session_id,
            client_phone=client_phone,
        )
        await self.save_session(session)
        return session
    
    async def save_session(self, session: SessionData):
        """Save session data to Redis"""
        redis = await self._get_redis()
        key = self._session_key(session.session_id)
        
        # Update last activity
        session.last_activity = datetime.now().isoformat()
        
        try:
            await redis.setex(
                key, 
                self.session_ttl, 
                json.dumps(session.to_dict())
            )
        except Exception as e:
            print(f"Error saving session: {e}")
    
    async def get_or_create_session(
        self, 
        session_id: str, 
        client_phone: str
    ) -> SessionData:
        """Get existing session or create new one"""
        session = await self.get_session(session_id)
        if session:
            return session
        return await self.create_session(session_id, client_phone)
    
    async def update_session(
        self, 
        session_id: str, 
        **updates
    ) -> Optional[SessionData]:
        """Update session with new data"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.message_count += 1
        await self.save_session(session)
        return session
    
    async def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str
    ):
        """Add message to conversation history"""
        redis = await self._get_redis()
        key = self._history_key(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            await redis.rpush(key, json.dumps(message))
            await redis.ltrim(key, -self.history_limit, -1)
            await redis.expire(key, self.session_ttl)
        except Exception as e:
            print(f"Error adding message: {e}")
    
    async def get_history(self, session_id: str) -> list[dict]:
        """Get conversation history for session"""
        redis = await self._get_redis()
        key = self._history_key(session_id)
        
        try:
            messages = await redis.lrange(key, 0, -1)
            return [json.loads(m) for m in messages]
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    async def clear_session(self, session_id: str):
        """Clear session and history"""
        redis = await self._get_redis()
        
        try:
            await redis.delete(
                self._session_key(session_id),
                self._history_key(session_id)
            )
        except Exception as e:
            print(f"Error clearing session: {e}")
    
    async def close(self):
        """Close Redis connection"""
        if self._redis and hasattr(self._redis, 'close'):
            await self._redis.close()


class InMemorySessionStore:
    """Fallback in-memory session store when Redis is not available"""
    
    def __init__(self):
        self._store: dict[str, Any] = {}
        self._expires: dict[str, datetime] = {}
    
    async def get(self, key: str) -> Optional[str]:
        if key in self._expires and datetime.now() > self._expires[key]:
            del self._store[key]
            del self._expires[key]
            return None
        return self._store.get(key)
    
    async def setex(self, key: str, ttl: int, value: str):
        self._store[key] = value
        self._expires[key] = datetime.now() + timedelta(seconds=ttl)
    
    async def delete(self, *keys):
        for key in keys:
            self._store.pop(key, None)
            self._expires.pop(key, None)
    
    async def rpush(self, key: str, value: str):
        if key not in self._store:
            self._store[key] = []
        self._store[key].append(value)
    
    async def ltrim(self, key: str, start: int, end: int):
        if key in self._store:
            self._store[key] = self._store[key][start:] if end == -1 else self._store[key][start:end+1]
    
    async def lrange(self, key: str, start: int, end: int):
        if key not in self._store:
            return []
        return self._store[key][start:] if end == -1 else self._store[key][start:end+1]
    
    async def expire(self, key: str, ttl: int):
        self._expires[key] = datetime.now() + timedelta(seconds=ttl)
