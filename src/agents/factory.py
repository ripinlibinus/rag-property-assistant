"""
Factory functions for creating agent instances with proper dependencies
"""

from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .orchestrator import OrchestratorAgent
from .property_agent import PropertyAgent
from .coach_agent import CoachAgent
from ..adapters.metaproperty import MetaPropertyAPIAdapter


def create_property_agent(
    api_url: str,
    api_token: Optional[str] = None,
    llm: Optional[ChatOpenAI] = None,
    embeddings: Optional[OpenAIEmbeddings] = None,
    enable_vector_search: bool = True,
) -> PropertyAgent:
    """
    Create a PropertyAgent with MetaProperty adapter.
    
    Args:
        api_url: MetaProperty API URL
        api_token: Optional API token for write operations
        llm: Optional LLM instance
        embeddings: Optional embeddings instance
        enable_vector_search: Whether to use ChromaDB for ranking
        
    Returns:
        Configured PropertyAgent
    """
    adapter = MetaPropertyAPIAdapter(
        api_url=api_url,
        api_token=api_token,
    )
    
    return PropertyAgent(
        data_adapter=adapter,
        llm=llm,
        embeddings=embeddings,
        enable_vector_search=enable_vector_search,
    )


def create_orchestrator(
    metaproperty_url: Optional[str] = None,
    metaproperty_token: Optional[str] = None,
    llm: Optional[ChatOpenAI] = None,
    include_property_agent: bool = True,
    include_coach_agent: bool = True,
) -> OrchestratorAgent:
    """
    Create an OrchestratorAgent with all sub-agents configured.
    
    Args:
        metaproperty_url: MetaProperty API URL (required for property agent)
        metaproperty_token: Optional API token for write operations
        llm: Optional LLM instance to share across agents
        include_property_agent: Whether to include property agent
        include_coach_agent: Whether to include coach agent
        
    Returns:
        Configured OrchestratorAgent
    """
    llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    property_agent = None
    if include_property_agent and metaproperty_url:
        property_agent = create_property_agent(
            api_url=metaproperty_url,
            api_token=metaproperty_token,
            llm=llm,
        )
    
    coach_agent = None
    if include_coach_agent:
        coach_agent = CoachAgent(llm=llm)
    
    return OrchestratorAgent(
        llm=llm,
        property_agent=property_agent,
        coach_agent=coach_agent,
    )


def create_orchestrator_from_env() -> OrchestratorAgent:
    """
    Create OrchestratorAgent using environment variables.
    
    Required env vars:
        - OPENAI_API_KEY
        
    Optional env vars:
        - METAPROPERTY_API_URL
        - METAPROPERTY_API_TOKEN
        - OPENAI_MODEL (default: gpt-4o-mini)
    """
    import os
    
    # Get config from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    metaproperty_url = os.getenv("METAPROPERTY_API_URL")
    metaproperty_token = os.getenv("METAPROPERTY_API_TOKEN")
    
    llm = ChatOpenAI(model=model, temperature=0)
    
    return create_orchestrator(
        metaproperty_url=metaproperty_url,
        metaproperty_token=metaproperty_token,
        llm=llm,
    )
