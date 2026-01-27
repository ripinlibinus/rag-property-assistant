"""
Hybrid Search - Combines API filtering with ChromaDB semantic re-ranking

Strategy:
1. API Search: Filter by structured criteria (price, bedrooms, location, type)
2. ChromaDB: Re-rank results by semantic relevance to user query

This gives us:
- Accurate filters from database (price range, bedroom count, etc.)
- Smart semantic matching for vague queries ("rumah nyaman", "taman luas")
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from cachetools import TTLCache

from ..adapters.base import Property, SearchCriteria, SearchResult
from ..utils.logging import get_search_logger
from ..utils.metrics import (
    SearchMetrics,
    Timer,
    get_metrics_collector,
)
from ..utils.ab_testing import get_ab_manager, SearchMethod

# Module logger
logger = get_search_logger()


# =============================================================================
# Embedding Cache - Reduce OpenAI API calls by ~80%
# =============================================================================

# Cache embeddings for 1 hour (3600 seconds), max 1000 queries
_embedding_cache: TTLCache = TTLCache(maxsize=1000, ttl=3600)


def get_cached_embedding(query: str, embeddings: OpenAIEmbeddings) -> List[float]:
    """
    Get embedding with caching to reduce API calls.

    Args:
        query: The text to embed
        embeddings: OpenAIEmbeddings instance

    Returns:
        List of floats representing the embedding vector
    """
    # Normalize query for better cache hits
    cache_key = query.strip().lower()

    if cache_key not in _embedding_cache:
        _embedding_cache[cache_key] = embeddings.embed_query(query)

    return _embedding_cache[cache_key]


def get_embedding_cache_stats() -> dict:
    """Get cache statistics for monitoring."""
    return {
        "size": len(_embedding_cache),
        "maxsize": _embedding_cache.maxsize,
        "ttl": _embedding_cache.ttl,
    }


@dataclass
class HybridSearchResult:
    """Result from hybrid search with semantic scores"""
    properties: List[Property]
    semantic_scores: dict[str, float]  # property_id -> score
    total: int
    api_count: int
    reranked: bool
    has_more: bool = False  # True if there are more results available (for pagination)


class HybridSearchService:
    """
    Hybrid search combining API filters with ChromaDB semantic re-ranking.

    Usage:
        hybrid = HybridSearchService(property_store)
        results = await hybrid.search(
            adapter=adapter,
            query="rumah taman luas dekat sekolah",
            min_price=500000000,
            max_price=1500000000,
            city="Medan"
        )
    """

    def __init__(
        self,
        property_store=None,
        embedding_model: str = "text-embedding-3-small",
        semantic_weight: float = 0.6,  # How much to weight semantic vs API order
    ):
        """
        Initialize hybrid search.

        Args:
            property_store: PropertyStore instance (optional, will create if needed)
            embedding_model: OpenAI embedding model
            semantic_weight: Weight for semantic ranking (0-1, higher = more semantic influence)
        """
        self.property_store = property_store
        self.semantic_weight = semantic_weight
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        return self._embeddings

    async def _fetch_urls_from_api(
        self,
        adapter,
        properties_by_source: dict[str, str],
    ) -> dict[str, str]:
        """
        Fetch URLs for properties from API based on their source type.

        This is a workaround when ChromaDB doesn't have url_view/slug metadata.
        Once ChromaDB is re-synced with these fields, this fetch will be skipped.

        Args:
            adapter: PropertyDataAdapter for API access
            properties_by_source: Dict mapping property_id -> source ("listing" or "project")

        Returns:
            Dict mapping property_id -> url_view
        """
        if not properties_by_source:
            return {}

        url_map = {}

        # Separate IDs by source type
        listing_ids = [pid for pid, src in properties_by_source.items() if src == "listing"]
        project_ids = [pid for pid, src in properties_by_source.items() if src in ("project", "proyek")]

        import httpx

        try:
            async with httpx.AsyncClient(
                base_url=adapter.api_url,
                headers={"Accept": "application/json"},
                timeout=10,
            ) as client:
                # Fetch listings from /api/v1/properties
                if listing_ids:
                    ids_param = ",".join(listing_ids)
                    response = await client.get(
                        "/api/v1/properties",
                        params={"ids": ids_param, "per_page": len(listing_ids)},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("data", []):
                            prop_id = str(item.get("id", ""))
                            url_view = item.get("url_view", "")
                            if prop_id and url_view:
                                url_map[prop_id] = url_view
                        logger.debug("fetch_listing_urls_success", count=len(listing_ids), found=len([k for k in url_map if k in listing_ids]))

                # Fetch projects from /api/v1/projects
                if project_ids:
                    ids_param = ",".join(project_ids)
                    response = await client.get(
                        "/api/v1/projects",
                        params={"ids": ids_param, "per_page": len(project_ids)},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        for item in data.get("data", []):
                            prop_id = str(item.get("id", ""))
                            url_view = item.get("url_view", "")
                            if prop_id and url_view:
                                url_map[prop_id] = url_view
                        logger.debug("fetch_project_urls_success", count=len(project_ids), found=len([k for k in url_map if k in project_ids]))

        except Exception as e:
            logger.warning("fetch_urls_from_api_failed", error=str(e), total_ids=len(properties_by_source))

        return url_map

    async def search(
        self,
        adapter,
        query: str,
        user_query: Optional[str] = None,  # Original user message for semantic search
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        source: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_bedrooms: Optional[int] = None,
        max_bedrooms: Optional[int] = None,
        min_floors: Optional[int] = None,
        max_floors: Optional[int] = None,
        amenities: Optional[list] = None,
        city: Optional[str] = None,
        in_complex: Optional[bool] = None,
        facing: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
        use_semantic_rerank: bool = True,
        user_id: Optional[str] = None,
        ab_method: Optional[SearchMethod] = None,
        # Geo parameters for smart location fallback
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = None,
        # Skip ChromaDB fallback when API returns empty (for testing location search)
        skip_chromadb_fallback: bool = False,
    ) -> HybridSearchResult:
        """
        Perform hybrid search with API filtering and semantic re-ranking.

        Args:
            adapter: PropertyDataAdapter for API access
            query: Search query (used for both API and semantic)
            property_type, listing_type, etc.: Filter criteria
            page: Page number (1-indexed) for pagination
            limit: Max results per page
            use_semantic_rerank: Whether to re-rank with ChromaDB
            user_id: User ID for A/B test assignment
            ab_method: Override A/B test method (for testing)

        Returns:
            HybridSearchResult with properties and semantic scores
        """
        from ..adapters.base import SearchCriteria, PropertyType, ListingType
        
        # Get A/B test method if not overridden
        if ab_method is None:
            ab_method = get_ab_manager().get_method(user_id)
        
        # Apply A/B test method settings
        effective_semantic_weight = ab_method.semantic_weight
        effective_use_rerank = ab_method.use_semantic_rerank and use_semantic_rerank
        
        # Initialize metrics
        metrics = SearchMetrics(
            query=query,
            user_id=user_id or "anonymous",
            method=ab_method.value,
        )
        total_timer = Timer()
        
        with total_timer:
            # Handle ChromaDB-only mode (skip API search)
            if not ab_method.use_api_search and self.property_store:
                metrics.method = "chromadb_only"
                result = await self._fallback_semantic_search(
                    adapter=adapter,
                    query=query,
                    user_query=user_query,
                    limit=limit,
                    source=source,
                )
                metrics.chromadb_results_count = result.total
                metrics.final_results_count = len(result.properties)
                metrics.total_latency_ms = total_timer.elapsed_ms
                metrics.reranking_applied = False
                get_metrics_collector().log_search(metrics)
                return result
            
            # Step 1: API Search with filters
            api_timer = Timer()
            with api_timer:
                # Enrich API query with amenities for text search
                # Since API doesn't have amenities filter, add to search query
                api_query = query
                if amenities:
                    # Add amenities to search query for full-text search
                    # This helps API find properties with CCTV, WiFi in description
                    amenity_terms = " ".join(amenities)
                    api_query = f"{query} {amenity_terms}"

                criteria = SearchCriteria(
                    query=api_query,
                    property_type=PropertyType(property_type) if property_type else None,
                    listing_type=ListingType(listing_type) if listing_type else None,
                    source=source,
                    min_price=min_price,
                    max_price=max_price,
                    min_bedrooms=min_bedrooms,
                    max_bedrooms=max_bedrooms,
                    min_floors=min_floors,
                    max_floors=max_floors,
                    amenities=amenities or [],
                    city=city,
                    in_complex=in_complex,
                    facing=facing,
                    page=page,
                    limit=limit * 2 if use_semantic_rerank else limit,  # Get more for re-ranking
                    # Geo parameters for smart location fallback
                    latitude=latitude,
                    longitude=longitude,
                    radius_km=radius_km,
                )
        
            api_result = await adapter.search(criteria)

            metrics.api_results_count = len(api_result.properties)
            metrics.api_latency_ms = api_timer.elapsed_ms

            # Note: Amenity prioritization is handled by semantic re-ranking (Step 3)
            # No need for keyword matching - multilingual embeddings handle cross-language similarity

        # Step 2: If API returns no results, try pure semantic search
        # (unless skip_chromadb_fallback is True - for testing location search accuracy)
        if not api_result.properties and self.property_store and not skip_chromadb_fallback:
            metrics.method = "chromadb_only"
            result = await self._fallback_semantic_search(
                adapter=adapter,
                query=query,
                user_query=user_query,
                limit=limit,
                source=source,
                amenities=amenities,
                property_type=property_type,
                listing_type=listing_type,
            )
            metrics.chromadb_results_count = result.total
            metrics.final_results_count = len(result.properties)
            metrics.total_latency_ms = total_timer.elapsed_ms
            metrics.reranking_applied = False

            # Log metrics
            get_metrics_collector().log_search(metrics)
            return result
        
        if not api_result.properties:
            metrics.final_results_count = 0
            metrics.total_latency_ms = total_timer.elapsed_ms
            get_metrics_collector().log_search(metrics)
            return HybridSearchResult(
                properties=[],
                semantic_scores={},
                total=0,
                api_count=0,
                reranked=False,
                has_more=False,
            )
        
        api_count = len(api_result.properties)
        
        # Step 3: Semantic Re-ranking (if enabled and property_store available)
        if effective_use_rerank and self.property_store:
            try:
                rerank_timer = Timer()
                with rerank_timer:
                    # Enrich query with amenities for better semantic matching
                    # This helps find properties with CCTV, WiFi, etc. mentioned in description
                    semantic_query = query
                    if amenities:
                        amenity_terms = " ".join(amenities)
                        semantic_query = f"{query} {amenity_terms}"

                    reranked = self._semantic_rerank(
                        query=semantic_query,
                        properties=api_result.properties,
                        limit=limit,
                        semantic_weight=effective_semantic_weight,
                    )
                
                # Calculate reranking changes (positions that changed)
                original_ids = [str(p.id) for p in api_result.properties[:limit]]
                reranked_ids = [str(p.id) for p in reranked["properties"]]
                reranking_changes = sum(1 for i, pid in enumerate(reranked_ids) if i < len(original_ids) and pid != original_ids[i])
                
                metrics.reranking_applied = True
                metrics.reranking_changes = reranking_changes
                metrics.reranking_latency_ms = rerank_timer.elapsed_ms
                metrics.chromadb_results_count = len(reranked["scores"])
                metrics.final_results_count = len(reranked["properties"])
                metrics.total_latency_ms = total_timer.elapsed_ms
                metrics.embedding_cache_hit = query.strip().lower() in _embedding_cache
                
                get_metrics_collector().log_search(metrics)

                return HybridSearchResult(
                    properties=reranked["properties"],
                    semantic_scores=reranked["scores"],
                    total=api_result.total,
                    api_count=api_count,
                    reranked=True,
                    has_more=api_result.has_more,
                )
            except Exception as e:
                logger.warning("semantic_rerank_failed", error=str(e), fallback="api_order")

        # Fallback: Return API results as-is
        metrics.reranking_applied = False
        metrics.final_results_count = len(api_result.properties[:limit])
        metrics.total_latency_ms = total_timer.elapsed_ms
        get_metrics_collector().log_search(metrics)

        return HybridSearchResult(
            properties=api_result.properties[:limit],
            semantic_scores={},
            total=api_result.total,
            api_count=api_count,
            reranked=False,
            has_more=api_result.has_more,
        )
    
    async def _fallback_semantic_search(
        self,
        adapter,
        query: str,
        user_query: Optional[str] = None,  # Original user message for semantic search
        limit: int = 10,
        source: Optional[str] = None,
        amenities: Optional[List[str]] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
    ):
        """
        Fallback to pure semantic search when API returns no results.

        Strategy:
        1. Search ChromaDB for semantically similar properties
        2. Filter by source if specified (project/listing)
        3. Filter by property_type if specified (house/apartment/warehouse/etc.)
        4. Filter by listing_type if specified (sale/rent)
        5. Filter by amenity keywords if specified (cctv, wifi, etc.)
        6. Build Property objects from ChromaDB metadata
           (ChromaDB has enough data for display: title, price, city, etc.)
        """
        if not self.property_store:
            return HybridSearchResult(
                properties=[],
                semantic_scores={},
                total=0,
                api_count=0,
                reranked=False,
                has_more=False,
            )

        # Build filter for ChromaDB (source, property_type, listing_type)
        chroma_filter = None
        filter_conditions = []

        if source:
            filter_conditions.append({"source": source})
        if property_type:
            filter_conditions.append({"property_type": property_type})
        if listing_type:
            filter_conditions.append({"listing_type": listing_type})

        if len(filter_conditions) == 1:
            chroma_filter = filter_conditions[0]
        elif len(filter_conditions) > 1:
            chroma_filter = {"$and": filter_conditions}

        # Use original user_query for semantic search (better for embeddings)
        # Fall back to extracted query if user_query not provided
        semantic_query = user_query or query

        query_embedding = get_cached_embedding(semantic_query, self.embeddings)

        # Search with higher k when amenities filter will be applied (need more candidates)
        # Semantic search alone can't guarantee keyword presence, so we fetch more and post-filter
        k_search = 100 if amenities else (limit * 2 if chroma_filter else limit)
        results = self.property_store.vector_store.similarity_search_by_vector_with_relevance_scores(
            embedding=query_embedding,
            k=k_search,
            filter=chroma_filter,
        )

        # Post-filter by amenities keywords if specified
        if amenities and results:
            # Amenity to Indonesian keyword mapping
            amenity_id_mapping = {
                "basketball_court": ["basket", "lapangan basket"],
                "swimming_pool": ["kolam renang", "pool", "swimming"],
                "gym": ["gym", "fitness", "fitnes"],
                "playground": ["playground", "taman bermain", "area bermain"],
                "tennis_court": ["tenis", "tennis", "lapangan tenis"],
                "jogging_track": ["jogging", "joging", "lari"],
                "security": ["security", "keamanan", "satpam"],
                "cctv": ["cctv"],
                "wifi": ["wifi", "wi-fi", "internet"],
                "ac": ["ac", "air conditioner"],
                "furnished": ["furnished", "perabot", "furnish"],
                "garden": ["taman", "garden"],
                "carport": ["carport", "garasi", "parkir"],
            }

            # Build keyword variations for matching
            amenity_keywords = []
            for a in amenities:
                a_lower = a.lower()
                # Add original and snake_case converted
                amenity_keywords.append(a_lower)
                amenity_keywords.append(a_lower.replace("_", " "))
                # Add Indonesian mappings if available
                if a_lower in amenity_id_mapping:
                    amenity_keywords.extend(amenity_id_mapping[a_lower])

            filtered_results = []
            for doc, score in results:
                doc_text = (doc.page_content or "").lower()
                if any(kw in doc_text for kw in amenity_keywords):
                    filtered_results.append((doc, score))

            logger.info(
                "semantic_fallback_search",
                query=semantic_query,
                amenities=amenities,
                raw_count=len(results),
                after_keyword_filter=len(filtered_results),
            )
            results = filtered_results
        else:
            logger.info(
                "semantic_fallback_search",
                query=semantic_query,
                amenities=amenities,
                found_count=len(results),
            )
        
        if not results:
            return HybridSearchResult(
                properties=[],
                semantic_scores={},
                total=0,
                api_count=0,
                reranked=False,
                has_more=False,
            )

        # Build Property objects from ChromaDB metadata
        from ..adapters.base import Property, PropertyType, ListingType

        properties = []
        semantic_scores = {}
        property_ids = []  # Collect IDs for URL enrichment

        for doc, score in results:
            meta = doc.metadata
            prop_id = meta.get("property_id")
            if not prop_id:
                continue

            # Map property_type string to enum
            prop_type_str = meta.get("property_type", "house")
            try:
                prop_type = PropertyType(prop_type_str)
            except ValueError:
                prop_type = PropertyType.HOUSE

            # Map listing_type string to enum
            listing_type_str = meta.get("listing_type", "sale")
            try:
                listing_type = ListingType(listing_type_str)
            except ValueError:
                listing_type = ListingType.SALE

            # Build minimal Property from metadata
            prop = Property(
                id=prop_id,
                source="metaproperty",  # Required field
                title=meta.get("title", "Unknown"),
                property_type=prop_type,
                listing_type=listing_type,
                price=meta.get("price", 0),
                location=meta.get("district", ""),
                city=meta.get("city", ""),
                bedrooms=meta.get("bedrooms"),
                bathrooms=meta.get("bathrooms"),
                land_area=meta.get("land_area"),
                building_area=meta.get("building_area"),
                source_type=meta.get("source", "listing"),
                url_view=meta.get("url_view", ""),  # Will be enriched from API
            )
            properties.append(prop)
            property_ids.append(str(prop_id))
            # Score is already relevance score (higher = better) from similarity_search_by_vector_with_relevance_scores
            semantic_scores[str(prop_id)] = score

            # Stop if we have enough
            if len(properties) >= limit:
                break

        # Enrich properties with URL from API (only if ChromaDB doesn't have url_view yet)
        # Once ChromaDB is re-synced with url_view/slug, this block will be skipped
        if properties and adapter:
            # Find properties that need URL enrichment (don't have url_view from metadata)
            properties_need_url = {
                str(prop.id): prop.source_type or "listing"
                for prop in properties
                if not prop.url_view  # Skip if already has url_view from ChromaDB
            }

            if properties_need_url:
                try:
                    url_map = await self._fetch_urls_from_api(adapter, properties_need_url)
                    for prop in properties:
                        if str(prop.id) in url_map:
                            prop.url_view = url_map[str(prop.id)]
                    logger.info("url_enrichment_success", needed=len(properties_need_url), found=len(url_map))
                except Exception as e:
                    logger.warning("url_enrichment_failed", error=str(e))
            else:
                logger.debug("url_enrichment_skipped", reason="all_properties_have_url_view")

        return HybridSearchResult(
            properties=properties,
            semantic_scores=semantic_scores,
            total=len(properties),
            api_count=0,  # No API results
            reranked=True,  # This is semantic-only
            has_more=False,  # Semantic-only doesn't support pagination yet
        )

    def _semantic_rerank(
        self,
        query: str,
        properties: List[Property],
        limit: int = 10,
        semantic_weight: Optional[float] = None,
    ) -> dict:
        """
        Re-rank properties using ChromaDB semantic similarity.
        
        Strategy:
        1. Get semantic scores from ChromaDB for each property
        2. Combine with API order (position score)
        3. Sort by combined score
        
        Args:
            query: Search query
            properties: Properties to re-rank
            limit: Max results to return
            semantic_weight: Weight for semantic vs API order (0-1). Uses instance default if None.
        """
        if not self.property_store:
            return {"properties": properties[:limit], "scores": {}}
        
        # Use provided weight or instance default
        weight = semantic_weight if semantic_weight is not None else self.semantic_weight
        
        # Get property IDs
        property_ids = [str(p.id) for p in properties]
        
        # Get semantic scores from ChromaDB
        semantic_scores = {}
        try:
            # Dynamic k based on API results - only fetch what we need
            # Add small buffer for re-ranking flexibility
            k_rerank = min(len(properties) + 5, 25)

            # Get cached embedding for the query
            query_embedding = get_cached_embedding(query, self.embeddings)

            # Search ChromaDB with pre-computed embedding (uses cache)
            results = self.property_store.vector_store.similarity_search_by_vector_with_relevance_scores(
                embedding=query_embedding,
                k=k_rerank,
            )
            
            # Map property_id to relevance score (higher = better match)
            for doc, score in results:
                prop_id = doc.metadata.get("property_id")
                if prop_id:
                    # Score is already relevance score from similarity_search_by_vector_with_relevance_scores
                    semantic_scores[str(prop_id)] = score
                    
        except Exception as e:
            logger.error("semantic_score_error", error=str(e), query=query)
            return {"properties": properties[:limit], "scores": {}}
        
        # Calculate combined scores
        scored_properties = []
        for i, prop in enumerate(properties):
            prop_id = str(prop.id)
            
            # API position score (earlier = better, normalize to 0-1)
            api_score = 1.0 - (i / len(properties))
            
            # Semantic score (from ChromaDB, default to 0 if not found)
            sem_score = semantic_scores.get(prop_id, 0.0)
            
            # Combined score using provided weight
            combined = (
                weight * sem_score +
                (1 - weight) * api_score
            )
            
            scored_properties.append({
                "property": prop,
                "api_score": api_score,
                "semantic_score": sem_score,
                "combined_score": combined,
            })
        
        # Sort by combined score (descending)
        scored_properties.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Build result
        reranked_properties = [sp["property"] for sp in scored_properties[:limit]]
        scores = {
            str(sp["property"].id): sp["semantic_score"] 
            for sp in scored_properties[:limit]
        }
        
        return {
            "properties": reranked_properties,
            "scores": scores,
        }
    
    def semantic_search_only(
        self,
        query: str,
        k: int = 10,
        property_type: Optional[str] = None,
        city: Optional[str] = None,
    ) -> List[str]:
        """
        Pure semantic search (ChromaDB only, no API).
        
        Returns list of property IDs ranked by semantic relevance.
        Useful for queries with no structured filters.
        """
        if not self.property_store:
            return []
        
        return self.property_store.search(
            query=query,
            k=k,
            property_type=property_type,
            city=city,
        )
