"""
MySQL Chat Memory

Persistent chat history storage using MetaProperty MySQL API.
Provides sliding window for token efficiency while keeping full history.
"""

import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)


@dataclass
class ChatMemoryConfig:
    """Configuration for chat memory"""
    api_url: str
    api_token: str
    max_messages: int = 20  # Max messages to load for context
    timeout: float = 30.0


class MySQLChatMemory:
    """
    Chat memory backed by MySQL via MetaProperty API.
    
    Features:
    - Persistent storage across sessions
    - Sliding window for token efficiency
    - Full history preserved in database
    - Automatic conversation creation
    
    Usage:
        memory = MySQLChatMemory(config)
        
        # Get context for LLM
        messages = memory.get_context_messages(thread_id)
        
        # Save messages after LLM response
        memory.save_message(thread_id, "user", "Hello")
        memory.save_message(thread_id, "assistant", "Hi there!")
    """
    
    def __init__(self, config: ChatMemoryConfig):
        self.config = config
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.config.api_url,
                headers={
                    "Authorization": f"Bearer {self.config.api_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=self.config.timeout,
            )
        return self._client
    
    def close(self):
        """Close HTTP client"""
        if self._client:
            self._client.close()
            self._client = None
    
    def get_context_messages(
        self, 
        thread_id: str, 
        limit: Optional[int] = None
    ) -> List[BaseMessage]:
        """
        Get recent messages for LLM context.
        
        Returns LangChain message objects ready for use with agent.
        
        Args:
            thread_id: Conversation thread ID
            limit: Max messages to retrieve (default from config)
            
        Returns:
            List of LangChain BaseMessage objects
        """
        limit = limit or self.config.max_messages
        
        try:
            response = self.client.get(
                f"/api/v1/chat/conversations/{thread_id}/messages",
                params={"limit": limit},
            )
            
            if response.status_code == 404:
                return []
            
            response.raise_for_status()
            data = response.json()
            
            messages = []
            for msg in data.get("data", []):
                lc_msg = self._to_langchain_message(msg)
                if lc_msg:
                    messages.append(lc_msg)
            
            return messages
            
        except httpx.HTTPError as e:
            print(f"Error fetching messages: {e}")
            return []
    
    def get_conversation_summary(self, thread_id: str) -> Optional[str]:
        """Get AI-generated summary of older conversation"""
        try:
            response = self.client.get(
                f"/api/v1/chat/conversations/{thread_id}",
            )
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("summary")
            
        except httpx.HTTPError:
            return None
    
    def save_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
        tool_call_id: Optional[str] = None,
        tool_calls: Optional[List[Dict]] = None,
        token_count: Optional[int] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Save a message to the conversation.
        
        Args:
            thread_id: Conversation thread ID
            role: Message role ('user', 'assistant', 'tool', 'system')
            content: Message content
            tool_name: For tool messages
            tool_call_id: For tool messages
            tool_calls: For assistant messages with tool calls
            token_count: Estimated token count
            metadata: Additional metadata
            
        Returns:
            True if saved successfully
        """
        try:
            payload = {
                "role": role,
                "content": content,
            }
            
            if tool_name:
                payload["tool_name"] = tool_name
            if tool_call_id:
                payload["tool_call_id"] = tool_call_id
            if tool_calls:
                payload["tool_calls"] = tool_calls
            if token_count:
                payload["token_count"] = token_count
            if metadata:
                payload["metadata"] = metadata
            
            response = self.client.post(
                f"/api/v1/chat/conversations/{thread_id}/messages",
                json=payload,
            )
            response.raise_for_status()
            return True
            
        except httpx.HTTPError as e:
            print(f"Error saving message: {e}")
            return False
    
    def save_messages_bulk(
        self,
        thread_id: str,
        messages: List[BaseMessage],
    ) -> bool:
        """
        Save multiple messages at once.
        
        Useful for saving the full agent turn (user + tool calls + response).
        """
        try:
            payload = {
                "messages": [
                    self._from_langchain_message(msg)
                    for msg in messages
                ]
            }
            
            response = self.client.post(
                f"/api/v1/chat/conversations/{thread_id}/messages/bulk",
                json=payload,
            )
            response.raise_for_status()
            return True
            
        except httpx.HTTPError as e:
            print(f"Error saving messages: {e}")
            return False
    
    def _to_langchain_message(self, msg: Dict) -> Optional[BaseMessage]:
        """Convert API message to LangChain message"""
        role = msg.get("role")
        content = msg.get("content", "")
        
        if role == "system":
            return SystemMessage(content=content)
        
        elif role == "user":
            return HumanMessage(content=content)
        
        elif role == "assistant":
            tool_calls = msg.get("tool_calls")
            if tool_calls:
                return AIMessage(content=content, tool_calls=tool_calls)
            return AIMessage(content=content)
        
        elif role == "tool":
            return ToolMessage(
                content=content,
                tool_call_id=msg.get("tool_call_id", ""),
                name=msg.get("tool_name", ""),
            )
        
        return None
    
    def _from_langchain_message(self, msg: BaseMessage) -> Dict:
        """Convert LangChain message to API format"""
        data = {
            "content": msg.content,
        }
        
        if isinstance(msg, SystemMessage):
            data["role"] = "system"
        
        elif isinstance(msg, HumanMessage):
            data["role"] = "user"
        
        elif isinstance(msg, AIMessage):
            data["role"] = "assistant"
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                data["tool_calls"] = msg.tool_calls
        
        elif isinstance(msg, ToolMessage):
            data["role"] = "tool"
            data["tool_call_id"] = msg.tool_call_id
            data["tool_name"] = msg.name
        
        return data


class SlidingWindowMemory:
    """
    Memory wrapper that combines:
    1. Summary of older messages (if available)
    2. Recent N messages from MySQL
    
    This provides context while staying within token limits.
    """
    
    def __init__(
        self,
        mysql_memory: MySQLChatMemory,
        max_recent_messages: int = 20,
        include_summary: bool = True,
    ):
        self.mysql = mysql_memory
        self.max_recent = max_recent_messages
        self.include_summary = include_summary
    
    def get_messages_for_llm(self, thread_id: str) -> List[BaseMessage]:
        """
        Get optimized message list for LLM context.
        
        Returns:
            [Optional: Summary of older context]
            + [Recent N messages]
        """
        messages = []
        
        # Get summary if enabled
        if self.include_summary:
            summary = self.mysql.get_conversation_summary(thread_id)
            if summary:
                messages.append(SystemMessage(
                    content=f"[PREVIOUS CONVERSATION SUMMARY]\n{summary}"
                ))
        
        # Get recent messages
        recent = self.mysql.get_context_messages(thread_id, self.max_recent)
        messages.extend(recent)
        
        return messages
    
    def save_turn(
        self,
        thread_id: str,
        user_message: str,
        assistant_messages: List[BaseMessage],
    ):
        """
        Save a complete conversation turn.
        
        Args:
            thread_id: Conversation thread ID
            user_message: The user's input
            assistant_messages: All messages from agent (may include tool calls)
        """
        # Save user message
        self.mysql.save_message(thread_id, "user", user_message)
        
        # Save assistant messages (including tool interactions)
        for msg in assistant_messages:
            if isinstance(msg, AIMessage):
                self.mysql.save_message(
                    thread_id,
                    "assistant",
                    msg.content,
                    tool_calls=msg.tool_calls if hasattr(msg, "tool_calls") else None,
                )
            elif isinstance(msg, ToolMessage):
                self.mysql.save_message(
                    thread_id,
                    "tool",
                    msg.content,
                    tool_name=msg.name,
                    tool_call_id=msg.tool_call_id,
                )


def create_mysql_memory(
    api_url: str,
    api_token: str,
    max_messages: int = 20,
) -> SlidingWindowMemory:
    """
    Factory function to create MySQL-backed chat memory.
    
    Args:
        api_url: MetaProperty API URL
        api_token: API authentication token
        max_messages: Max recent messages to include in context
        
    Returns:
        SlidingWindowMemory instance
    """
    config = ChatMemoryConfig(
        api_url=api_url,
        api_token=api_token,
        max_messages=max_messages,
    )
    mysql_memory = MySQLChatMemory(config)
    return SlidingWindowMemory(mysql_memory, max_recent_messages=max_messages)
