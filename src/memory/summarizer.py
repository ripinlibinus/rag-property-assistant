"""
Conversation Summarization Service

Responsible for:
- Generating summaries of completed conversations using LLM
- Extracting key topics, intents, and entities
- Saving summaries to long-term memory (PostgreSQL)
"""

from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


# Pydantic model for structured output
class ConversationSummaryOutput(BaseModel):
    """Structured output from conversation summarization"""
    summary: str = Field(description="Concise summary of the conversation in 2-3 sentences")
    primary_intent: str = Field(description="Main intent: property_search, coaching_sales, coaching_knowledge, greeting, or other")
    key_topics: List[str] = Field(description="List of main topics discussed (max 5)")
    entities_mentioned: List[str] = Field(description="Property IDs, locations, prices mentioned")
    outcome: str = Field(description="Outcome: resolved, pending, escalated, or abandoned")
    extracted_preferences: Optional[dict] = Field(
        default=None, 
        description="User preferences extracted (locations, budget, property_types, features)"
    )


SUMMARIZATION_PROMPT = """You are an AI assistant tasked with summarizing a real estate chatbot conversation.

Analyze the following conversation and extract key information.

CONVERSATION:
{conversation}

Provide a structured summary with:
1. **summary**: A concise 2-3 sentence summary of what happened
2. **primary_intent**: Main intent (property_search, coaching_sales, coaching_knowledge, greeting, other)
3. **key_topics**: List of main topics (max 5 items)
4. **entities_mentioned**: Any property IDs, specific locations, or prices mentioned
5. **outcome**: 
   - "resolved" if the user's query was answered
   - "pending" if there's follow-up needed
   - "escalated" if transferred to human
   - "abandoned" if user left without resolution
6. **extracted_preferences**: If the user mentioned preferences, extract:
   - locations: List of preferred areas
   - budget: {{min: number, max: number}} in IDR
   - property_types: rumah, ruko, tanah, apartment
   - features: bedrooms, bathrooms, specific features

Respond in JSON format only. Use Indonesian for the summary if the conversation was in Indonesian."""


@dataclass
class Message:
    """Simple message structure for conversation history"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[datetime] = None


class ConversationSummarizer:
    """
    Service for summarizing conversations and extracting insights.
    
    Usage:
        summarizer = ConversationSummarizer()
        result = await summarizer.summarize(messages)
        
        # Save to database
        with db.session() as session:
            repo = ConversationSummaryRepository(session)
            repo.create(
                client_id=client_id,
                session_id=session_id,
                summary=result.summary,
                ...
            )
    """
    
    def __init__(
        self, 
        llm: Optional[ChatOpenAI] = None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize the summarizer.
        
        Args:
            llm: Language model to use
            model: Model name if llm not provided
        """
        self.llm = llm or ChatOpenAI(model=model, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=ConversationSummaryOutput)
    
    def _format_conversation(self, messages: List[Message]) -> str:
        """Format message list into readable conversation"""
        lines = []
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            lines.append(f"{role}: {msg.content}")
        return "\n".join(lines)
    
    async def summarize(
        self, 
        messages: List[Message]
    ) -> ConversationSummaryOutput:
        """
        Summarize a conversation.
        
        Args:
            messages: List of messages in the conversation
        
        Returns:
            ConversationSummaryOutput with summary and extracted info
        """
        if not messages:
            return ConversationSummaryOutput(
                summary="Empty conversation",
                primary_intent="other",
                key_topics=[],
                entities_mentioned=[],
                outcome="abandoned",
            )
        
        conversation_text = self._format_conversation(messages)
        prompt = SUMMARIZATION_PROMPT.format(conversation=conversation_text)
        
        try:
            response = await self.llm.ainvoke([
                SystemMessage(content="You are a helpful assistant that outputs valid JSON."),
                HumanMessage(content=prompt),
            ])
            
            # Parse JSON response
            result = self.parser.parse(response.content)
            return ConversationSummaryOutput(**result)
            
        except Exception as e:
            print(f"Summarization error: {e}")
            # Return basic summary on error
            return ConversationSummaryOutput(
                summary=f"Conversation with {len(messages)} messages (summarization failed)",
                primary_intent="other",
                key_topics=[],
                entities_mentioned=[],
                outcome="resolved",
            )
    
    async def summarize_from_session(
        self,
        session_data: Any,  # SessionData from session.py
        message_history: List[dict],  # Raw message dicts
    ) -> ConversationSummaryOutput:
        """
        Summarize from session data format.
        
        Args:
            session_data: SessionData object
            message_history: List of message dicts with 'role' and 'content'
        """
        messages = [
            Message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
            )
            for msg in message_history
        ]
        return await self.summarize(messages)
    
    def extract_preferences(
        self, 
        summary_output: ConversationSummaryOutput
    ) -> dict:
        """
        Extract user preferences from summary for profile update.
        
        Returns dict suitable for ClientProfileRepository.update_preferences()
        """
        if not summary_output.extracted_preferences:
            return {}
        
        prefs = summary_output.extracted_preferences
        result = {}
        
        if prefs.get("locations"):
            result["locations"] = prefs["locations"]
        if prefs.get("budget"):
            result["budget_range"] = prefs["budget"]
        if prefs.get("property_types"):
            result["property_types"] = prefs["property_types"]
        if prefs.get("features"):
            result["features"] = prefs["features"]
        
        return result


class ConversationLifecycleManager:
    """
    Manages the full lifecycle of a conversation:
    - Tracks active sessions
    - Triggers summarization on session end
    - Saves to long-term memory
    - Updates client profile with learned preferences
    """
    
    def __init__(
        self,
        summarizer: Optional[ConversationSummarizer] = None,
        db_manager: Optional[Any] = None,  # DatabaseManager
    ):
        self.summarizer = summarizer or ConversationSummarizer()
        self.db_manager = db_manager
    
    async def end_conversation(
        self,
        session_id: str,
        client_phone: str,
        messages: List[Message],
        started_at: datetime,
    ) -> Optional[UUID]:
        """
        End a conversation and save summary to long-term memory.
        
        Args:
            session_id: Unique session identifier
            client_phone: Client's phone number
            messages: All messages in the conversation
            started_at: When the conversation started
        
        Returns:
            UUID of created ConversationSummary, or None on error
        """
        if not self.db_manager:
            print("Warning: No database manager configured, skipping save")
            return None
        
        # Generate summary
        summary_output = await self.summarizer.summarize(messages)
        
        # Import here to avoid circular imports
        from .repository import (
            ClientProfileRepository, 
            ConversationSummaryRepository
        )
        
        try:
            with self.db_manager.session() as session:
                # Get or create client profile
                client_repo = ClientProfileRepository(session)
                profile, created = client_repo.get_or_create(client_phone)
                
                # Update engagement metrics
                client_repo.increment_engagement(
                    profile.id,
                    messages=len(messages),
                    conversations=1,
                )
                
                # Update preferences if extracted
                prefs = self.summarizer.extract_preferences(summary_output)
                if prefs:
                    client_repo.update_preferences(
                        profile.id,
                        locations=prefs.get("locations"),
                        budget_range=prefs.get("budget_range"),
                        property_types=prefs.get("property_types"),
                        features=prefs.get("features"),
                    )
                
                # Save conversation summary
                summary_repo = ConversationSummaryRepository(session)
                conv_summary = summary_repo.create(
                    client_id=profile.id,
                    session_id=session_id,
                    summary=summary_output.summary,
                    started_at=started_at,
                    primary_intent=summary_output.primary_intent,
                    key_topics=summary_output.key_topics,
                    entities_mentioned=summary_output.entities_mentioned,
                    message_count=len(messages),
                    outcome=summary_output.outcome,
                )
                
                return conv_summary.id
                
        except Exception as e:
            print(f"Error saving conversation summary: {e}")
            return None
    
    async def get_client_context(
        self, 
        client_phone: str, 
        limit: int = 5
    ) -> str:
        """
        Get context from previous conversations for a client.
        
        Returns formatted context string for LLM prompts.
        """
        if not self.db_manager:
            return "No previous context available."
        
        from .repository import (
            ClientProfileRepository,
            ConversationSummaryRepository,
        )
        
        try:
            with self.db_manager.session() as session:
                client_repo = ClientProfileRepository(session)
                profile = client_repo.get_by_phone(client_phone)
                
                if not profile:
                    return "New client, no previous interactions."
                
                # Get conversation history context
                summary_repo = ConversationSummaryRepository(session)
                history_context = summary_repo.get_context_for_client(
                    profile.id, 
                    limit=limit
                )
                
                # Build full context
                context_parts = []
                
                # Client profile info
                if profile.preferred_locations:
                    context_parts.append(
                        f"Preferred locations: {', '.join(profile.preferred_locations)}"
                    )
                if profile.budget_range:
                    budget = profile.budget_range
                    context_parts.append(
                        f"Budget: Rp {budget.get('min', 0):,.0f} - Rp {budget.get('max', 0):,.0f}"
                    )
                if profile.preferred_property_types:
                    context_parts.append(
                        f"Looking for: {', '.join(profile.preferred_property_types)}"
                    )
                
                if context_parts:
                    profile_context = "CLIENT PROFILE:\n" + "\n".join(context_parts)
                else:
                    profile_context = ""
                
                if history_context and history_context != "No previous conversation history.":
                    full_context = f"{profile_context}\n\nPREVIOUS CONVERSATIONS:\n{history_context}"
                else:
                    full_context = profile_context or "No previous context available."
                
                return full_context.strip()
                
        except Exception as e:
            print(f"Error getting client context: {e}")
            return "Error retrieving context."
