"""
Repository Pattern Implementation for Long-Term Memory

Provides CRUD operations for:
- ClientProfile: User preferences and learned data
- ConversationSummary: Summarized conversation history
- PropertyInteraction: User-property interactions
- AgentMetrics: Performance metrics for evaluation
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from contextlib import contextmanager

from sqlalchemy import create_engine, select, update, delete, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import (
    Base,
    ClientProfile,
    ConversationSummary,
    PropertyInteraction,
    AgentMetrics,
)


class DatabaseManager:
    """
    Manages database connections and provides session context.
    
    Usage:
        db = DatabaseManager("postgresql://...")
        with db.session() as session:
            # do database operations
    """
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database manager.
        
        Args:
            database_url: PostgreSQL connection string
            echo: If True, log all SQL statements
        """
        self.engine = create_engine(database_url, echo=echo)
        self._session_factory = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
    
    @contextmanager
    def session(self):
        """
        Provide a transactional scope around a series of operations.
        
        Usage:
            with db.session() as session:
                profile = ClientProfileRepository(session).get_by_phone("08123...")
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class ClientProfileRepository:
    """
    Repository for ClientProfile CRUD operations.
    
    Manages long-term client data including:
    - Contact information
    - Learned preferences (locations, budget, property types)
    - Engagement metrics
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        phone_number: str,
        name: Optional[str] = None,
        role: str = "buyer",
        agent_id: Optional[int] = None,
    ) -> ClientProfile:
        """
        Create a new client profile.
        
        Args:
            phone_number: Client's phone number (unique)
            name: Client's name
            role: "buyer", "seller", or "agent"
            agent_id: Link to agent in main system
        
        Returns:
            Created ClientProfile
        """
        profile = ClientProfile(
            phone_number=phone_number,
            name=name,
            role=role,
            agent_id=agent_id,
            preferred_locations=[],
            preferred_property_types=[],
            preferred_features=[],
        )
        self.session.add(profile)
        self.session.flush()  # Get the ID immediately
        return profile
    
    def get_by_id(self, profile_id: UUID) -> Optional[ClientProfile]:
        """Get client profile by ID"""
        return self.session.get(ClientProfile, profile_id)
    
    def get_by_phone(self, phone_number: str) -> Optional[ClientProfile]:
        """Get client profile by phone number"""
        stmt = select(ClientProfile).where(ClientProfile.phone_number == phone_number)
        return self.session.scalar(stmt)
    
    def get_or_create(
        self, 
        phone_number: str, 
        name: Optional[str] = None
    ) -> tuple[ClientProfile, bool]:
        """
        Get existing profile or create new one.
        
        Returns:
            Tuple of (profile, created) where created is True if new
        """
        profile = self.get_by_phone(phone_number)
        if profile:
            return profile, False
        return self.create(phone_number=phone_number, name=name), True
    
    def update(
        self,
        profile_id: UUID,
        **kwargs
    ) -> Optional[ClientProfile]:
        """
        Update client profile fields.
        
        Args:
            profile_id: Profile UUID
            **kwargs: Fields to update (name, role, preferred_locations, etc.)
        
        Returns:
            Updated profile or None if not found
        """
        profile = self.get_by_id(profile_id)
        if not profile:
            return None
        
        for key, value in kwargs.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.updated_at = datetime.utcnow()
        self.session.flush()
        return profile
    
    def update_preferences(
        self,
        profile_id: UUID,
        locations: Optional[List[str]] = None,
        budget_range: Optional[dict] = None,
        property_types: Optional[List[str]] = None,
        features: Optional[List[str]] = None,
    ) -> Optional[ClientProfile]:
        """
        Update client preferences (learned from conversations).
        
        Merges new preferences with existing ones.
        """
        profile = self.get_by_id(profile_id)
        if not profile:
            return None
        
        if locations:
            existing = profile.preferred_locations or []
            profile.preferred_locations = list(set(existing + locations))
        
        if budget_range:
            profile.budget_range = budget_range
        
        if property_types:
            existing = profile.preferred_property_types or []
            profile.preferred_property_types = list(set(existing + property_types))
        
        if features:
            existing = profile.preferred_features or []
            profile.preferred_features = list(set(existing + features))
        
        profile.updated_at = datetime.utcnow()
        self.session.flush()
        return profile
    
    def increment_engagement(
        self, 
        profile_id: UUID, 
        messages: int = 0, 
        conversations: int = 0
    ) -> Optional[ClientProfile]:
        """Increment engagement counters"""
        profile = self.get_by_id(profile_id)
        if not profile:
            return None
        
        profile.total_messages = (profile.total_messages or 0) + messages
        profile.total_conversations = (profile.total_conversations or 0) + conversations
        profile.last_active_at = datetime.utcnow()
        profile.updated_at = datetime.utcnow()
        self.session.flush()
        return profile
    
    def list_recent(self, limit: int = 20) -> List[ClientProfile]:
        """List recently active client profiles"""
        stmt = (
            select(ClientProfile)
            .order_by(ClientProfile.last_active_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))
    
    def delete(self, profile_id: UUID) -> bool:
        """Delete a client profile"""
        stmt = delete(ClientProfile).where(ClientProfile.id == profile_id)
        result = self.session.execute(stmt)
        return result.rowcount > 0


class ConversationSummaryRepository:
    """
    Repository for ConversationSummary CRUD operations.
    
    Manages summarized conversation history for:
    - Context retrieval in future conversations
    - Long-term memory of past interactions
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        client_id: UUID,
        session_id: str,
        summary: str,
        started_at: datetime,
        primary_intent: Optional[str] = None,
        key_topics: Optional[List[str]] = None,
        entities_mentioned: Optional[List[str]] = None,
        message_count: int = 0,
        outcome: str = "resolved",
    ) -> ConversationSummary:
        """
        Create a new conversation summary.
        
        Args:
            client_id: Reference to ClientProfile
            session_id: Unique session identifier
            summary: LLM-generated summary text
            started_at: When conversation started
            primary_intent: Main intent of conversation
            key_topics: Topics discussed
            entities_mentioned: Property IDs, locations, etc.
            message_count: Total messages in conversation
            outcome: "resolved", "pending", "escalated"
        
        Returns:
            Created ConversationSummary
        """
        conv_summary = ConversationSummary(
            client_id=client_id,
            session_id=session_id,
            summary=summary,
            started_at=started_at,
            ended_at=datetime.utcnow(),
            primary_intent=primary_intent,
            key_topics=key_topics or [],
            entities_mentioned=entities_mentioned or [],
            message_count=message_count,
            outcome=outcome,
        )
        self.session.add(conv_summary)
        self.session.flush()
        return conv_summary
    
    def get_by_id(self, summary_id: UUID) -> Optional[ConversationSummary]:
        """Get conversation summary by ID"""
        return self.session.get(ConversationSummary, summary_id)
    
    def get_by_session_id(self, session_id: str) -> Optional[ConversationSummary]:
        """Get conversation summary by session ID"""
        stmt = select(ConversationSummary).where(
            ConversationSummary.session_id == session_id
        )
        return self.session.scalar(stmt)
    
    def get_client_history(
        self, 
        client_id: UUID, 
        limit: int = 10
    ) -> List[ConversationSummary]:
        """
        Get recent conversation history for a client.
        
        Args:
            client_id: Client profile ID
            limit: Maximum summaries to return
        
        Returns:
            List of conversation summaries, most recent first
        """
        stmt = (
            select(ConversationSummary)
            .where(ConversationSummary.client_id == client_id)
            .order_by(ConversationSummary.started_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))
    
    def get_context_for_client(
        self, 
        client_id: UUID, 
        limit: int = 5
    ) -> str:
        """
        Get formatted context string for LLM from recent conversations.
        
        Returns a formatted summary of recent interactions.
        """
        summaries = self.get_client_history(client_id, limit)
        if not summaries:
            return "No previous conversation history."
        
        context_parts = []
        for s in summaries:
            date_str = s.started_at.strftime("%Y-%m-%d")
            topics = ", ".join(s.key_topics) if s.key_topics else "general"
            context_parts.append(
                f"[{date_str}] Intent: {s.primary_intent or 'unknown'}, "
                f"Topics: {topics}\n{s.summary}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    def update(
        self, 
        summary_id: UUID, 
        **kwargs
    ) -> Optional[ConversationSummary]:
        """Update conversation summary fields"""
        summary = self.get_by_id(summary_id)
        if not summary:
            return None
        
        for key, value in kwargs.items():
            if hasattr(summary, key):
                setattr(summary, key, value)
        
        self.session.flush()
        return summary
    
    def delete(self, summary_id: UUID) -> bool:
        """Delete a conversation summary"""
        stmt = delete(ConversationSummary).where(ConversationSummary.id == summary_id)
        result = self.session.execute(stmt)
        return result.rowcount > 0


class PropertyInteractionRepository:
    """
    Repository for PropertyInteraction tracking.
    
    Tracks how users interact with properties for:
    - Recommendation improvements
    - Analytics and insights
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        client_id: UUID,
        property_id: int,
        interaction_type: str,
        search_query: Optional[str] = None,
        match_score: Optional[float] = None,
    ) -> PropertyInteraction:
        """
        Record a property interaction.
        
        Args:
            client_id: Client profile ID
            property_id: Property ID from main database
            interaction_type: "viewed", "inquired", "favorited", "shared"
            search_query: Query that led to this property
            match_score: How well property matched query (0-1)
        """
        interaction = PropertyInteraction(
            client_id=client_id,
            property_id=property_id,
            interaction_type=interaction_type,
            search_query=search_query,
            match_score=match_score,
        )
        self.session.add(interaction)
        self.session.flush()
        return interaction
    
    def add_feedback(
        self,
        interaction_id: UUID,
        feedback: str,
        reason: Optional[str] = None,
    ) -> Optional[PropertyInteraction]:
        """
        Add user feedback to an interaction.
        
        Args:
            interaction_id: Interaction ID
            feedback: "positive", "negative", "neutral"
            reason: Optional reason text
        """
        interaction = self.session.get(PropertyInteraction, interaction_id)
        if not interaction:
            return None
        
        interaction.feedback = feedback
        interaction.feedback_reason = reason
        self.session.flush()
        return interaction
    
    def get_client_interactions(
        self,
        client_id: UUID,
        interaction_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[PropertyInteraction]:
        """Get property interactions for a client"""
        stmt = select(PropertyInteraction).where(
            PropertyInteraction.client_id == client_id
        )
        if interaction_type:
            stmt = stmt.where(PropertyInteraction.interaction_type == interaction_type)
        
        stmt = stmt.order_by(PropertyInteraction.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt))
    
    def get_property_interactions(
        self,
        property_id: int,
        limit: int = 100,
    ) -> List[PropertyInteraction]:
        """Get all interactions for a specific property"""
        stmt = (
            select(PropertyInteraction)
            .where(PropertyInteraction.property_id == property_id)
            .order_by(PropertyInteraction.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))


class AgentMetricsRepository:
    """
    Repository for AgentMetrics - Performance tracking for thesis analysis.
    
    Stores per-request metrics including:
    - Latency (total, LLM, retrieval)
    - Token usage and cost
    - Accuracy metrics
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(
        self,
        session_id: str,
        request_id: str,
        user_message: str,
        detected_intent: Optional[str] = None,
        routed_to: Optional[str] = None,
        response: Optional[str] = None,
        total_latency_ms: Optional[int] = None,
        llm_latency_ms: Optional[int] = None,
        retrieval_latency_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        estimated_cost_usd: Optional[float] = None,
    ) -> AgentMetrics:
        """Record a new metrics entry"""
        metrics = AgentMetrics(
            session_id=session_id,
            request_id=request_id,
            user_message=user_message,
            detected_intent=detected_intent,
            routed_to=routed_to,
            response=response,
            total_latency_ms=total_latency_ms,
            llm_latency_ms=llm_latency_ms,
            retrieval_latency_ms=retrieval_latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_tokens=output_tokens,
            estimated_cost_usd=estimated_cost_usd,
        )
        self.session.add(metrics)
        self.session.flush()
        return metrics
    
    def update_evaluation(
        self,
        request_id: str,
        actual_intent: Optional[str] = None,
        relevance_score: Optional[float] = None,
        is_correct: Optional[bool] = None,
        error_type: Optional[str] = None,
    ) -> Optional[AgentMetrics]:
        """
        Update metrics with evaluation results.
        
        Used after manual or automated evaluation of responses.
        """
        stmt = select(AgentMetrics).where(AgentMetrics.request_id == request_id)
        metrics = self.session.scalar(stmt)
        if not metrics:
            return None
        
        if actual_intent is not None:
            metrics.actual_intent = actual_intent
        if relevance_score is not None:
            metrics.relevance_score = relevance_score
        if is_correct is not None:
            metrics.is_correct = is_correct
        if error_type is not None:
            metrics.error_type = error_type
        
        self.session.flush()
        return metrics
    
    def get_session_metrics(self, session_id: str) -> List[AgentMetrics]:
        """Get all metrics for a session"""
        stmt = (
            select(AgentMetrics)
            .where(AgentMetrics.session_id == session_id)
            .order_by(AgentMetrics.created_at)
        )
        return list(self.session.scalars(stmt))
    
    def get_metrics_by_intent(
        self, 
        intent: str, 
        limit: int = 100
    ) -> List[AgentMetrics]:
        """Get metrics filtered by detected intent"""
        stmt = (
            select(AgentMetrics)
            .where(AgentMetrics.detected_intent == intent)
            .order_by(AgentMetrics.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(stmt))
    
    def get_aggregate_stats(self) -> dict:
        """
        Get aggregate statistics for analysis.
        
        Returns dict with:
        - total_requests
        - avg_latency_ms
        - total_tokens
        - total_cost_usd
        - accuracy (if evaluated)
        """
        from sqlalchemy import func
        
        stmt = select(
            func.count(AgentMetrics.id).label("total_requests"),
            func.avg(AgentMetrics.total_latency_ms).label("avg_latency_ms"),
            func.sum(AgentMetrics.input_tokens).label("total_input_tokens"),
            func.sum(AgentMetrics.output_tokens).label("total_output_tokens"),
            func.sum(AgentMetrics.estimated_cost_usd).label("total_cost_usd"),
        )
        
        result = self.session.execute(stmt).first()
        
        # Calculate accuracy for evaluated items
        accuracy_stmt = select(
            func.count(AgentMetrics.id).filter(AgentMetrics.is_correct == True).label("correct"),
            func.count(AgentMetrics.id).filter(AgentMetrics.is_correct != None).label("evaluated"),
        )
        accuracy_result = self.session.execute(accuracy_stmt).first()
        
        accuracy = None
        if accuracy_result.evaluated and accuracy_result.evaluated > 0:
            accuracy = accuracy_result.correct / accuracy_result.evaluated
        
        return {
            "total_requests": result.total_requests or 0,
            "avg_latency_ms": float(result.avg_latency_ms or 0),
            "total_input_tokens": result.total_input_tokens or 0,
            "total_output_tokens": result.total_output_tokens or 0,
            "total_cost_usd": float(result.total_cost_usd or 0),
            "accuracy": accuracy,
        }
