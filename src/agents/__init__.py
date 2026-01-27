"""Agents module - Contains all agent implementations"""

from .orchestrator import OrchestratorAgent
from .property_agent import PropertyAgent
from .coach_agent import CoachAgent
from .react_agent import ReActPropertyAgent, create_property_react_agent
from .tools import create_all_tools, create_property_tools, create_knowledge_tools
from .factory import (
    create_orchestrator,
    create_orchestrator_from_env,
    create_property_agent,
)

__all__ = [
    # Old pattern (for backward compatibility)
    "OrchestratorAgent",
    "PropertyAgent",
    "CoachAgent",
    "create_orchestrator",
    "create_orchestrator_from_env",
    "create_property_agent",
    # New ReAct pattern (recommended)
    "ReActPropertyAgent",
    "create_property_react_agent",
    "create_all_tools",
    "create_property_tools",
    "create_knowledge_tools",
]
