"""
Data Adapters Package - Universal interface for property data sources
"""

from .base import PropertyDataAdapter, Property, PropertyCreate, PropertyUpdate, SearchCriteria
from .metaproperty import MetaPropertyAPIAdapter

__all__ = [
    "PropertyDataAdapter",
    "Property", 
    "PropertyCreate",
    "PropertyUpdate",
    "SearchCriteria",
    "MetaPropertyAPIAdapter",
]
