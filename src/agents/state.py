"""
State definitions for LangGraph agents
Defines the shared state that flows through the agent graph
"""

from typing import TypedDict, Annotated, Sequence, Literal, Optional
from dataclasses import dataclass, field
from langchain_core.messages import BaseMessage
import operator


# Reducer for message list - appends new messages
def add_messages(left: list[BaseMessage], right: list[BaseMessage]) -> list[BaseMessage]:
    """Merge two lists of messages"""
    return left + right


class AgentState(TypedDict):
    """
    Main state that flows through the LangGraph
    All agents share and update this state
    """
    # Conversation
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_input: str
    session_id: str
    client_phone: str
    
    # Routing
    intent: Optional[str]  # "property_search", "property_update", "coaching", "greeting", etc.
    confidence: float
    routed_to: Optional[str]  # Which agent is handling
    
    # Language detection
    language: Optional[str]  # "id" for Indonesian, "en" for English
    extracted_info: Optional[dict]  # Extracted info from intent classification
    
    # Context
    client_profile: Optional[dict]  # Loaded from long-term memory
    conversation_context: Optional[str]  # Summary of recent conversation
    
    # Agent Outputs
    retrieved_properties: Optional[list[dict]]
    property_action_result: Optional[dict]
    coaching_response: Optional[str]
    
    # Final Output
    response: Optional[str]
    
    # Metrics (for thesis evaluation)
    start_time: float
    metrics: dict


# Intent types for routing
INTENT_TYPES = Literal[
    "property_search",      # User looking for properties
    "property_update",      # Agent wants to update listing
    "property_description", # Generate marketing description
    "coaching_sales",       # Sales tips and techniques
    "coaching_knowledge",   # Real estate knowledge
    "coaching_motivation",  # Motivational support
    "greeting",             # Hello, thanks, etc.
    "general",              # General conversation
    "out_of_scope",         # Not related to real estate
]


@dataclass
class SearchCriteria:
    """Parsed property search criteria from user query"""
    property_type: Optional[str] = None  # "rumah", "ruko", "apartment", "tanah"
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    min_land_area: Optional[float] = None
    max_land_area: Optional[float] = None
    min_building_area: Optional[float] = None
    max_building_area: Optional[float] = None
    features: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class PropertySearchResult:
    """Property search result with relevance info"""
    property_id: int
    title: str
    property_type: str
    price: float
    location: str
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    land_area: Optional[float]
    building_area: Optional[float]
    features: list[str]
    images: list[str]
    
    # Relevance
    semantic_score: float  # Vector similarity
    filter_score: float    # SQL filter match
    combined_score: float
    match_reason: str      # Why this matches the query
    
    def to_dict(self) -> dict:
        return self.__dict__


@dataclass  
class CoachingResponse:
    """Structured coaching response"""
    category: str  # "sales", "knowledge", "motivation"
    topic: str
    main_response: str
    tips: list[str]
    source: Optional[str]  # Knowledge base reference
