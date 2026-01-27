"""
SQLite Chat Memory

Local SQLite-based chat history storage for the chatbot.
Provides persistent conversation storage with sliding window for token efficiency.

This is the LOCAL storage - no dependency on external APIs.
For production, can be migrated to PostgreSQL.
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from contextlib import contextmanager

from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)

from ..utils.logging import get_logger

# Module logger
logger = get_logger("rag.memory")


# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "chat_history.db"


@dataclass
class SQLiteMemoryConfig:
    """Configuration for SQLite memory"""
    db_path: Path = DEFAULT_DB_PATH
    max_messages: int = 20  # Max messages to load for context


class SQLiteChatMemory:
    """
    Chat memory backed by local SQLite database.
    
    Features:
    - Persistent storage across sessions
    - Sliding window for token efficiency
    - Full history preserved in database
    - No external API dependency
    
    Usage:
        memory = SQLiteChatMemory()
        
        # Save messages
        memory.save_message(thread_id, "user", "Hello")
        memory.save_message(thread_id, "assistant", "Hi there!")
        
        # Get context for LLM
        messages = memory.get_context_messages(thread_id)
    """
    
    def __init__(self, config: Optional[SQLiteMemoryConfig] = None):
        self.config = config or SQLiteMemoryConfig()
        self._ensure_db_exists()
        self._create_tables()
    
    def _ensure_db_exists(self):
        """Ensure database directory exists"""
        self.config.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(str(self.config.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    channel TEXT DEFAULT 'cli',
                    title TEXT,
                    summary TEXT,
                    message_count INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    last_message_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_name TEXT,
                    tool_call_id TEXT,
                    tool_calls TEXT,
                    token_count INTEGER,
                    metadata TEXT,
                    sequence INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            """)
            
            # Indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                ON messages(conversation_id, sequence)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_thread
                ON conversations(thread_id)
            """)
            # Index for user isolation queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_user
                ON conversations(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_thread_user
                ON conversations(thread_id, user_id)
            """)
    
    def get_or_create_conversation(
        self,
        thread_id: str,
        user_id: str = "anonymous",
    ) -> int:
        """
        Get existing conversation or create new one.

        IMPORTANT: user_id is now enforced for proper isolation.
        Each user should have their own conversations.

        Args:
            thread_id: Unique thread identifier
            user_id: User identifier (required for isolation, default "anonymous")

        Returns:
            Conversation ID
        """
        # Warn if using anonymous user (for debugging)
        if user_id == "anonymous":
            logger.warning(
                "conversation_anonymous_user",
                thread_id=thread_id,
                hint="Consider passing explicit user_id for proper isolation",
            )

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Include user_id in lookup for proper isolation
            cursor.execute(
                "SELECT id FROM conversations WHERE thread_id = ? AND user_id = ?",
                (thread_id, user_id)
            )
            row = cursor.fetchone()

            if row:
                return row["id"]

            # Create new conversation for this user
            cursor.execute(
                """INSERT INTO conversations (thread_id, user_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?)""",
                (thread_id, user_id, datetime.now(), datetime.now())
            )

            logger.info(
                "conversation_created",
                thread_id=thread_id,
                user_id=user_id,
                conversation_id=cursor.lastrowid,
            )

            return cursor.lastrowid
    
    def get_context_messages(
        self,
        thread_id: str,
        limit: Optional[int] = None,
        user_id: str = "anonymous",
    ) -> List[BaseMessage]:
        """
        Get recent messages for LLM context.

        Returns LangChain message objects ready for use with agent.
        Ensures valid message ordering for OpenAI API:
        - ToolMessages must follow AIMessage with tool_calls

        Args:
            thread_id: Conversation thread ID
            limit: Max messages to return
            user_id: User ID for isolation (required)
        """
        limit = limit or self.config.max_messages

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get conversation with user_id for proper isolation
            cursor.execute(
                "SELECT id FROM conversations WHERE thread_id = ? AND user_id = ?",
                (thread_id, user_id)
            )
            conv = cursor.fetchone()

            if not conv:
                return []

            # Get recent messages (newest first, then reverse)
            cursor.execute(
                """SELECT role, content, tool_name, tool_call_id, tool_calls
                   FROM messages
                   WHERE conversation_id = ?
                   ORDER BY sequence DESC
                   LIMIT ?""",
                (conv["id"], limit)
            )
            rows = cursor.fetchall()

            # Reverse to get chronological order
            rows = list(reversed(rows))

            messages = []
            for row in rows:
                msg = self._row_to_langchain_message(row)
                if msg:
                    messages.append(msg)

            # Validate and fix message sequence for OpenAI API compatibility
            messages = self._validate_message_sequence(messages)

            return messages

    def _validate_message_sequence(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Validate message sequence for OpenAI API compatibility.

        Rules:
        1. ToolMessage must follow an AIMessage with tool_calls
        2. Remove orphaned ToolMessages at the start
        3. Remove ToolMessages without matching tool_call_id
        """
        if not messages:
            return messages

        # Find first valid starting point (skip orphaned ToolMessages)
        start_idx = 0
        for i, msg in enumerate(messages):
            if isinstance(msg, ToolMessage):
                # Check if there's a preceding AIMessage with matching tool_call
                has_matching_ai = False
                for j in range(i - 1, -1, -1):
                    if isinstance(messages[j], AIMessage):
                        if hasattr(messages[j], 'tool_calls') and messages[j].tool_calls:
                            # Check if tool_call_id matches
                            tool_call_ids = [tc.get('id') or tc.get('tool_call_id')
                                           for tc in messages[j].tool_calls]
                            if msg.tool_call_id in tool_call_ids:
                                has_matching_ai = True
                        break

                if not has_matching_ai:
                    start_idx = i + 1
            else:
                # Found a non-tool message, this is a valid start
                break

        # Return from valid start point
        validated = messages[start_idx:]

        # Second pass: remove any remaining orphaned tool messages
        result = []
        pending_tool_calls = set()

        for msg in validated:
            if isinstance(msg, AIMessage):
                # Track tool_call_ids from this message
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tc_id = tc.get('id') or tc.get('tool_call_id')
                        if tc_id:
                            pending_tool_calls.add(tc_id)
                result.append(msg)
            elif isinstance(msg, ToolMessage):
                # Only include if we have a matching pending tool call
                if msg.tool_call_id in pending_tool_calls:
                    result.append(msg)
                    pending_tool_calls.discard(msg.tool_call_id)
                # Skip orphaned tool messages silently
            else:
                result.append(msg)

        return result
    
    def get_conversation_summary(self, thread_id: str) -> Optional[str]:
        """Get AI-generated summary of older conversation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT summary FROM conversations WHERE thread_id = ?",
                (thread_id,)
            )
            row = cursor.fetchone()
            return row["summary"] if row else None
    
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
        user_id: Optional[str] = None,
    ) -> int:
        """
        Save a message to the conversation.
        
        Returns:
            Message ID
        """
        conv_id = self.get_or_create_conversation(thread_id, user_id)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get next sequence number
            cursor.execute(
                "SELECT COALESCE(MAX(sequence), 0) + 1 FROM messages WHERE conversation_id = ?",
                (conv_id,)
            )
            sequence = cursor.fetchone()[0]
            
            # Insert message
            cursor.execute(
                """INSERT INTO messages 
                   (conversation_id, role, content, tool_name, tool_call_id, 
                    tool_calls, token_count, metadata, sequence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    conv_id,
                    role,
                    content,
                    tool_name,
                    tool_call_id,
                    json.dumps(tool_calls) if tool_calls else None,
                    token_count,
                    json.dumps(metadata) if metadata else None,
                    sequence,
                    datetime.now(),
                )
            )
            message_id = cursor.lastrowid
            
            # Update conversation stats
            cursor.execute(
                """UPDATE conversations 
                   SET message_count = message_count + 1,
                       total_tokens = total_tokens + COALESCE(?, 0),
                       last_message_at = ?,
                       updated_at = ?
                   WHERE id = ?""",
                (token_count, datetime.now(), datetime.now(), conv_id)
            )
            
            # Auto-set title from first user message
            if sequence == 1 and role == "user":
                title = content[:100] + "..." if len(content) > 100 else content
                cursor.execute(
                    "UPDATE conversations SET title = ? WHERE id = ?",
                    (title, conv_id)
                )
            
            return message_id
    
    def update_summary(self, thread_id: str, summary: str):
        """Update conversation summary"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET summary = ?, updated_at = ? WHERE thread_id = ?",
                (summary, datetime.now(), thread_id)
            )
    
    def get_conversation_stats(self, thread_id: str) -> Optional[Dict]:
        """Get conversation statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT thread_id, title, message_count, total_tokens, 
                          status, last_message_at, created_at
                   FROM conversations WHERE thread_id = ?""",
                (thread_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict]:
        """
        List conversations for a specific user.

        IMPORTANT: user_id is REQUIRED for proper isolation.
        Each user can only see their own conversations.

        Args:
            user_id: User identifier (REQUIRED)
            limit: Max conversations to return
            offset: Pagination offset

        Returns:
            List of conversation dicts
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """SELECT thread_id, title, message_count, last_message_at, created_at
                   FROM conversations
                   WHERE user_id = ? AND status = 'active'
                   ORDER BY last_message_at DESC
                   LIMIT ? OFFSET ?""",
                (user_id, limit, offset)
            )

            return [dict(row) for row in cursor.fetchall()]
    
    def delete_conversation(self, thread_id: str):
        """Soft delete a conversation"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE conversations SET status = 'deleted', updated_at = ? WHERE thread_id = ?",
                (datetime.now(), thread_id)
            )

    def get_older_messages(
        self,
        thread_id: str,
        offset: int = 20,
        limit: int = 50,
        user_id: str = "anonymous",
    ) -> List[Dict]:
        """
        Get older messages beyond the sliding window for summarization.

        Args:
            thread_id: Conversation thread ID
            offset: Skip this many recent messages (the sliding window)
            limit: Max older messages to retrieve
            user_id: User ID for isolation

        Returns:
            List of message dicts with role and content
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get conversation with user_id for proper isolation
            cursor.execute(
                "SELECT id FROM conversations WHERE thread_id = ? AND user_id = ?",
                (thread_id, user_id)
            )
            conv = cursor.fetchone()

            if not conv:
                return []

            # Get older messages (skip recent 'offset' messages)
            cursor.execute(
                """SELECT role, content
                   FROM messages
                   WHERE conversation_id = ?
                   ORDER BY sequence ASC
                   LIMIT ? OFFSET 0""",
                (conv["id"], limit)
            )

            # Calculate which messages are "older" (before the sliding window)
            cursor.execute(
                "SELECT COUNT(*) as total FROM messages WHERE conversation_id = ?",
                (conv["id"],)
            )
            total = cursor.fetchone()["total"]

            if total <= offset:
                return []  # Not enough messages to have "older" ones

            # Get messages that are before the sliding window
            older_count = total - offset
            cursor.execute(
                """SELECT role, content
                   FROM messages
                   WHERE conversation_id = ?
                   ORDER BY sequence ASC
                   LIMIT ?""",
                (conv["id"], min(older_count, limit))
            )

            return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]

    def delete_older_messages(
        self,
        thread_id: str,
        keep_recent: int = 20,
        user_id: str = "anonymous",
    ) -> int:
        """
        Delete older messages after summarization to save space.

        Args:
            thread_id: Conversation thread ID
            keep_recent: Number of recent messages to keep
            user_id: User ID for isolation

        Returns:
            Number of deleted messages
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get conversation
            cursor.execute(
                "SELECT id FROM conversations WHERE thread_id = ? AND user_id = ?",
                (thread_id, user_id)
            )
            conv = cursor.fetchone()

            if not conv:
                return 0

            # Get the sequence number threshold
            cursor.execute(
                """SELECT sequence FROM messages
                   WHERE conversation_id = ?
                   ORDER BY sequence DESC
                   LIMIT 1 OFFSET ?""",
                (conv["id"], keep_recent - 1)
            )
            row = cursor.fetchone()

            if not row:
                return 0

            threshold_sequence = row["sequence"]

            # Delete messages with sequence < threshold
            cursor.execute(
                """DELETE FROM messages
                   WHERE conversation_id = ? AND sequence < ?""",
                (conv["id"], threshold_sequence)
            )

            deleted = cursor.rowcount

            # Update message count
            cursor.execute(
                """UPDATE conversations
                   SET message_count = (SELECT COUNT(*) FROM messages WHERE conversation_id = ?),
                       updated_at = ?
                   WHERE id = ?""",
                (conv["id"], datetime.now(), conv["id"])
            )

            logger.info(
                "older_messages_deleted",
                thread_id=thread_id,
                deleted_count=deleted,
                kept_recent=keep_recent,
            )

            return deleted
    
    def _row_to_langchain_message(self, row: sqlite3.Row) -> Optional[BaseMessage]:
        """Convert database row to LangChain message"""
        role = row["role"]
        content = row["content"]
        
        if role == "system":
            return SystemMessage(content=content)
        
        elif role == "user":
            return HumanMessage(content=content)
        
        elif role == "assistant":
            tool_calls_json = row["tool_calls"]
            if tool_calls_json:
                tool_calls = json.loads(tool_calls_json)
                return AIMessage(content=content, tool_calls=tool_calls)
            return AIMessage(content=content)
        
        elif role == "tool":
            return ToolMessage(
                content=content,
                tool_call_id=row["tool_call_id"] or "",
                name=row["tool_name"] or "",
            )
        
        return None


class SlidingWindowMemory:
    """
    Memory wrapper that combines:
    1. Summary of older messages (if available)
    2. Recent N messages from SQLite

    This provides context while staying within token limits.

    Features:
    - Auto-summarization when conversation exceeds threshold
    - Summary stored in database for persistence
    - Optional cleanup of old messages after summarization
    """

    # Configuration
    SUMMARIZE_THRESHOLD = 50  # Trigger summarization when message count > this
    SUMMARY_PROMPT = """Summarize the following conversation between a user and a property assistant.
Focus on:
1. Properties the user was interested in (location, type, price range)
2. Key preferences mentioned (bedrooms, features, budget)
3. Any decisions or conclusions reached

Keep the summary concise (max 300 words) but include important details.

Conversation:
{conversation}

Summary:"""

    def __init__(
        self,
        sqlite_memory: SQLiteChatMemory,
        max_recent_messages: int = 20,
        include_summary: bool = True,
        auto_summarize: bool = True,
        delete_after_summarize: bool = False,
        llm=None,
    ):
        """
        Initialize SlidingWindowMemory.

        Args:
            sqlite_memory: SQLiteChatMemory instance
            max_recent_messages: Number of recent messages to include in context
            include_summary: Whether to include summary in context
            auto_summarize: Automatically summarize when threshold exceeded
            delete_after_summarize: Delete old messages after summarization
            llm: LLM instance for summarization (lazy loaded if not provided)
        """
        self.db = sqlite_memory
        self.max_recent = max_recent_messages
        self.include_summary = include_summary
        self.auto_summarize = auto_summarize
        self.delete_after_summarize = delete_after_summarize
        self._llm = llm
    
    def get_messages_for_llm(
        self,
        thread_id: str,
        user_id: str = "anonymous",
    ) -> List[BaseMessage]:
        """
        Get optimized message list for LLM context.

        Args:
            thread_id: Conversation thread ID
            user_id: User ID for isolation (REQUIRED for proper isolation)

        Returns:
            [Optional: Summary of older context]
            + [Recent N messages]
        """
        messages = []

        # Get summary if enabled
        if self.include_summary:
            summary = self.db.get_conversation_summary(thread_id)
            if summary:
                messages.append(SystemMessage(
                    content=f"[PREVIOUS CONVERSATION SUMMARY]\n{summary}"
                ))

        # Get recent messages with user isolation
        recent = self.db.get_context_messages(thread_id, self.max_recent, user_id=user_id)
        messages.extend(recent)

        return messages
    
    def save_turn(
        self,
        thread_id: str,
        user_message: str,
        assistant_messages: List[BaseMessage],
        user_id: Optional[str] = None,
    ):
        """
        Save a complete conversation turn.

        Args:
            thread_id: Conversation thread ID
            user_message: The user's input
            assistant_messages: All messages from agent (may include tool calls)
            user_id: Optional user ID

        Also triggers auto-summarization if enabled and threshold exceeded.
        """
        effective_user_id = user_id or "anonymous"

        # Save user message
        self.db.save_message(thread_id, "user", user_message, user_id=user_id)

        # Save assistant messages (including tool interactions)
        for msg in assistant_messages:
            if isinstance(msg, AIMessage):
                tool_calls = None
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls = msg.tool_calls
                self.db.save_message(
                    thread_id,
                    "assistant",
                    msg.content,
                    tool_calls=tool_calls,
                    user_id=user_id,
                )
            elif isinstance(msg, ToolMessage):
                self.db.save_message(
                    thread_id,
                    "tool",
                    msg.content,
                    tool_name=msg.name,
                    tool_call_id=msg.tool_call_id,
                    user_id=user_id,
                )

        # Trigger auto-summarization if needed
        if self.auto_summarize:
            self.maybe_summarize(thread_id, user_id=effective_user_id)
    
    def save_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        **kwargs
    ) -> int:
        """Direct save message to database"""
        return self.db.save_message(thread_id, role, content, **kwargs)

    @property
    def llm(self):
        """Lazy load LLM for summarization."""
        if self._llm is None:
            from langchain_openai import ChatOpenAI
            self._llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        return self._llm

    def maybe_summarize(
        self,
        thread_id: str,
        user_id: str = "anonymous",
    ) -> bool:
        """
        Check if conversation needs summarization and trigger if needed.

        Args:
            thread_id: Conversation thread ID
            user_id: User ID for isolation

        Returns:
            True if summarization was performed, False otherwise
        """
        if not self.auto_summarize:
            return False

        # Check message count
        stats = self.db.get_conversation_stats(thread_id)
        if not stats:
            return False

        message_count = stats.get("message_count", 0)
        if message_count <= self.SUMMARIZE_THRESHOLD:
            return False

        # Check if we already have a summary (avoid re-summarizing)
        existing_summary = self.db.get_conversation_summary(thread_id)

        # Get older messages to summarize
        older_messages = self.db.get_older_messages(
            thread_id,
            offset=self.max_recent,
            limit=100,  # Max messages to include in summary
            user_id=user_id,
        )

        if not older_messages:
            return False

        logger.info(
            "summarization_triggered",
            thread_id=thread_id,
            message_count=message_count,
            older_messages=len(older_messages),
        )

        # Generate summary
        new_summary = self._generate_summary(older_messages, existing_summary)

        if new_summary:
            # Save summary to database
            self.db.update_summary(thread_id, new_summary)

            # Optionally delete old messages
            if self.delete_after_summarize:
                self.db.delete_older_messages(
                    thread_id,
                    keep_recent=self.max_recent,
                    user_id=user_id,
                )

            logger.info(
                "summarization_completed",
                thread_id=thread_id,
                summary_length=len(new_summary),
            )
            return True

        return False

    def _generate_summary(
        self,
        messages: List[Dict],
        existing_summary: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate summary of older messages using LLM.

        Args:
            messages: List of message dicts with role and content
            existing_summary: Previous summary to incorporate

        Returns:
            Generated summary or None if failed
        """
        try:
            # Format conversation for summarization
            conversation_text = []

            # Include existing summary if available
            if existing_summary:
                conversation_text.append(f"[Previous Summary]: {existing_summary}\n")

            for msg in messages:
                role = msg["role"]
                content = msg["content"]

                if role == "user":
                    conversation_text.append(f"User: {content}")
                elif role == "assistant":
                    # Truncate long assistant responses
                    if len(content) > 500:
                        content = content[:500] + "..."
                    conversation_text.append(f"Assistant: {content}")
                elif role == "tool":
                    # Summarize tool results briefly
                    if len(content) > 200:
                        content = content[:200] + "..."
                    conversation_text.append(f"[Tool Result]: {content}")

            full_conversation = "\n".join(conversation_text)

            # Generate summary using LLM
            prompt = self.SUMMARY_PROMPT.format(conversation=full_conversation)
            response = self.llm.invoke(prompt)

            return response.content.strip()

        except Exception as e:
            logger.error("summarization_failed", error=str(e))
            return None

    def force_summarize(
        self,
        thread_id: str,
        user_id: str = "anonymous",
    ) -> Optional[str]:
        """
        Force summarization regardless of message count.

        Args:
            thread_id: Conversation thread ID
            user_id: User ID for isolation

        Returns:
            Generated summary or None if failed
        """
        older_messages = self.db.get_older_messages(
            thread_id,
            offset=self.max_recent,
            limit=100,
            user_id=user_id,
        )

        if not older_messages:
            return None

        existing_summary = self.db.get_conversation_summary(thread_id)
        new_summary = self._generate_summary(older_messages, existing_summary)

        if new_summary:
            self.db.update_summary(thread_id, new_summary)
            return new_summary

        return None


def create_sqlite_memory(
    db_path: Optional[Path] = None,
    max_messages: int = 20,
    auto_summarize: bool = True,
    delete_after_summarize: bool = False,
) -> SlidingWindowMemory:
    """
    Factory function to create SQLite-backed chat memory.

    Args:
        db_path: Path to SQLite database file (default: data/chat_history.db)
        max_messages: Max recent messages to include in context
        auto_summarize: Automatically summarize when threshold exceeded
        delete_after_summarize: Delete old messages after summarization

    Returns:
        SlidingWindowMemory instance with summarization support
    """
    config = SQLiteMemoryConfig(
        db_path=db_path or DEFAULT_DB_PATH,
        max_messages=max_messages,
    )
    sqlite_memory = SQLiteChatMemory(config)
    return SlidingWindowMemory(
        sqlite_memory,
        max_recent_messages=max_messages,
        auto_summarize=auto_summarize,
        delete_after_summarize=delete_after_summarize,
    )
