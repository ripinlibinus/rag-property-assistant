"""
Database models for Long-Term Memory System
Stores client profiles, conversation history, and learned preferences
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, JSON,
    ForeignKey, Index, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class ClientProfile(Base):
    """
    Stores long-term client information and learned preferences
    Used for personalization and context across conversations
    """
    __tablename__ = "client_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100))
    
    # Learned Preferences (extracted from conversations)
    preferred_locations = Column(JSON, default=list)  # ["Sunggal", "Medan Selayang"]
    budget_range = Column(JSON)  # {"min": 500000000, "max": 1500000000}
    preferred_property_types = Column(JSON, default=list)  # ["rumah", "ruko"]
    preferred_features = Column(JSON, default=list)  # ["3KT", "garasi", "dekat sekolah"]
    
    # Profile Data
    role = Column(String(20))  # "buyer", "seller", "agent"
    agent_id = Column(Integer)  # Link to agent in main system (if applicable)
    
    # Engagement Metrics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    last_active_at = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversations = relationship("ConversationSummary", back_populates="client")
    
    __table_args__ = (
        Index("ix_client_role", "role"),
        Index("ix_client_last_active", "last_active_at"),
    )


class ConversationSummary(Base):
    """
    Stores summarized conversations for context retrieval
    Used to maintain conversation continuity across sessions
    """
    __tablename__ = "conversation_summaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False)
    session_id = Column(String(100), nullable=False)
    
    # Conversation Summary
    summary = Column(Text, nullable=False)  # LLM-generated summary
    key_topics = Column(JSON, default=list)  # ["pencarian rumah", "negosiasi harga"]
    entities_mentioned = Column(JSON, default=list)  # Property IDs, locations, etc.
    
    # Intent & Outcome
    primary_intent = Column(String(50))  # "property_search", "coaching", etc.
    outcome = Column(String(50))  # "resolved", "pending", "escalated"
    
    # Metrics
    message_count = Column(Integer, default=0)
    duration_seconds = Column(Integer)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    client = relationship("ClientProfile", back_populates="conversations")
    
    __table_args__ = (
        Index("ix_conv_client_id", "client_id"),
        Index("ix_conv_session_id", "session_id"),
        Index("ix_conv_started_at", "started_at"),
    )


class PropertyInteraction(Base):
    """
    Tracks client interactions with specific properties
    Used for recommendation and analytics
    """
    __tablename__ = "property_interactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client_profiles.id"), nullable=False)
    property_id = Column(Integer, nullable=False)  # Links to main property database
    
    # Interaction Type
    interaction_type = Column(String(30), nullable=False)  # "viewed", "inquired", "favorited", "shared"
    
    # Context
    search_query = Column(Text)  # Query that led to this property
    match_score = Column(Float)  # How well it matched the query (0-1)
    
    # Feedback
    feedback = Column(String(20))  # "positive", "negative", "neutral"
    feedback_reason = Column(Text)  # "terlalu mahal", "lokasi tidak cocok"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_prop_int_client_id", "client_id"),
        Index("ix_prop_int_property_id", "property_id"),
        Index("ix_prop_int_type", "interaction_type"),
    )


class AgentMetrics(Base):
    """
    Stores evaluation metrics for thesis analysis
    Captures per-request performance data
    """
    __tablename__ = "agent_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request Info
    session_id = Column(String(100), nullable=False)
    request_id = Column(String(100), nullable=False, unique=True)
    
    # Input
    user_message = Column(Text, nullable=False)
    detected_intent = Column(String(50))
    actual_intent = Column(String(50))  # For labeled test data
    
    # Routing
    routed_to = Column(String(50))  # "property_agent", "coach_agent", etc.
    
    # Response
    response = Column(Text)
    response_tokens = Column(Integer)
    
    # Performance
    total_latency_ms = Column(Integer)  # Total response time
    llm_latency_ms = Column(Integer)  # Time in LLM calls
    retrieval_latency_ms = Column(Integer)  # Time in vector search
    
    # Cost
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    estimated_cost_usd = Column(Float)
    
    # Quality (for evaluation)
    relevance_score = Column(Float)  # 0-5, manual or LLM-judged
    is_correct = Column(Boolean)  # For test cases with known answers
    error_type = Column(String(50))  # If failed, what kind of error
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("ix_metrics_session", "session_id"),
        Index("ix_metrics_intent", "detected_intent"),
        Index("ix_metrics_routed_to", "routed_to"),
        Index("ix_metrics_created", "created_at"),
    )


def create_tables(database_url: str):
    """Create all tables in the database"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session"""
    Session = sessionmaker(bind=engine)
    return Session()
