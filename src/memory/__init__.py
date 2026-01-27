"""Memory module - Session management and long-term storage"""

from .models import ClientProfile, ConversationSummary, PropertyInteraction, AgentMetrics
from .session import SessionManager, SessionData
from .repository import (
    DatabaseManager,
    ClientProfileRepository,
    ConversationSummaryRepository,
    PropertyInteractionRepository,
    AgentMetricsRepository,
)
from .summarizer import (
    ConversationSummarizer,
    ConversationLifecycleManager,
    ConversationSummaryOutput,
    Message,
)
from .sqlite_memory import (
    SQLiteChatMemory,
    SlidingWindowMemory,
    SQLiteMemoryConfig,
    create_sqlite_memory,
)

__all__ = [
    # Models
    "ClientProfile",
    "ConversationSummary", 
    "PropertyInteraction",
    "AgentMetrics",
    # Session
    "SessionManager",
    "SessionData",
    # Repository
    "DatabaseManager",
    "ClientProfileRepository",
    "ConversationSummaryRepository",
    "PropertyInteractionRepository",
    "AgentMetricsRepository",
    # Summarizer
    "ConversationSummarizer",
    "ConversationLifecycleManager",
    "ConversationSummaryOutput",
    "Message",
    # SQLite Memory
    "SQLiteChatMemory",
    "SlidingWindowMemory",
    "SQLiteMemoryConfig",
    "create_sqlite_memory",
]
