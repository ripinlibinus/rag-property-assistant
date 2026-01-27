"""
Knowledge Module

Contains ChromaDB vector stores for:
- KnowledgeStore: Sales techniques, real estate knowledge, motivation
- PropertyStore: Property semantic search (title + description)
- HybridSearchService: Combines API filter + ChromaDB semantic re-ranking
"""

from .knowledge_store import KnowledgeStore, create_knowledge_store
from .property_store import PropertyStore, create_property_store
from .hybrid_search import (
    HybridSearchService,
    HybridSearchResult,
    get_cached_embedding,
    get_embedding_cache_stats,
)

__all__ = [
    "KnowledgeStore",
    "create_knowledge_store",
    "PropertyStore",
    "create_property_store",
    "HybridSearchService",
    "HybridSearchResult",
    "get_cached_embedding",
    "get_embedding_cache_stats",
]