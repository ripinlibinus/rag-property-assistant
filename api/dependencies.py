"""
FastAPI Dependencies - Dependency Injection for ReAct Agent
"""
from typing import Optional
from functools import lru_cache

from .config import get_settings


# Global agent instance (lazy-loaded)
_agent_instance = None


def get_property_adapter():
    """Get or create the property data adapter"""
    from src.adapters.metaproperty import MetaPropertyAPIAdapter

    settings = get_settings()
    return MetaPropertyAPIAdapter(
        api_url=settings.metaproperty_api_url,
        api_token=settings.metaproperty_api_token,
    )


def get_agent():
    """
    Get or create the ReAct property agent.
    Uses singleton pattern for efficiency.
    """
    global _agent_instance

    if _agent_instance is None:
        from src.agents.react_agent import create_property_react_agent

        settings = get_settings()
        adapter = get_property_adapter()

        _agent_instance = create_property_react_agent(
            property_adapter=adapter,
            model_name=settings.openai_model,
            enable_knowledge=True,
            enable_memory=True,
            db_path=settings.database_path,
        )

    return _agent_instance


def reset_agent():
    """Reset the agent instance (useful for testing)"""
    global _agent_instance
    _agent_instance = None
