"""
Agent Tools - Proper Tool Definitions for LangGraph ReAct Agent

These tools are what makes this a REAL agent vs hardcoded chain:
- LLM decides which tool to call based on user intent
- Tools have schemas that LLM can understand
- ReAct loop: think → call tool → observe result → repeat

Now with Hybrid Search:
- API filtering for structured criteria (price, bedrooms, location)
- ChromaDB semantic re-ranking for relevance to user query
"""

import os
import asyncio
from typing import Optional, List
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from ..adapters.base import (
    PropertyDataAdapter,
    SearchCriteria,
    PropertyType,
    ListingType,
)
from ..knowledge import PropertyStore, HybridSearchService
from ..utils.logging import get_agent_logger
from ..utils.metrics import ToolMetrics, Timer, get_metrics_collector

# Module logger
logger = get_agent_logger()


# Helper function to run async code in sync context
def run_async(coro):
    """Run async coroutine in sync context, handling event loop properly"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        # No running loop, create new one
        return asyncio.run(coro)
    else:
        # There's a running loop - use nest_asyncio to allow nested calls
        import nest_asyncio
        nest_asyncio.apply()
        # Create a new loop for this specific call to avoid conflicts
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()


# ============================================================================
# Tool Input Schemas (Pydantic models for structured input)
# ============================================================================

class SearchPropertiesInput(BaseModel):
    """Input schema for property search tool - NO location, use search_properties_by_location for that"""
    user_query: str = Field(
        description="""REQUIRED: The original user message/question exactly as they typed it.
This is used for semantic search to find relevant properties.
Do NOT modify or extract keywords - pass the EXACT user input.

Example: User says "carikan rumah dengan fasilitas cctv di medan"
→ user_query="carikan rumah dengan fasilitas cctv di medan" (exact copy)"""
    )
    query: Optional[str] = Field(
        default=None,
        description="""Optional extracted keywords for API text search.

DO NOT use for location search - use search_properties_by_location instead.

Examples:
- "furnished apartment" → query="furnished"
- "rumah dengan kolam renang" → query="kolam renang"
- "ruko 3 lantai" → query="3 lantai"
- "house with swimming pool" → query="swimming pool"
"""
    )
    property_type: Optional[str] = Field(
        default=None,
        description="Type of property: 'house', 'shophouse', 'land', 'apartment', 'warehouse'"
    )
    listing_type: Optional[str] = Field(
        default=None,
        description="""Listing type: 'sale' or 'rent'. MUST be set based on user intent.

SALE keywords (listing_type='sale'):
- Indonesian: "dijual", "jual", "beli", "pembelian", "harga jual", "untuk dijual"
- English: "for sale", "buy", "purchase", "selling"

RENT keywords (listing_type='rent'):
- Indonesian: "disewa", "sewa", "kontrak", "dikontrakkan", "per bulan", "per tahun", "bulanan", "tahunan"
- English: "for rent", "rental", "lease", "renting"

IMPORTANT: If user query contains ANY of these keywords, you MUST set listing_type accordingly.
Examples:
- "rumah dijual di cemara" → listing_type="sale"
- "ruko disewa di sunggal" → listing_type="rent"
- "cari rumah untuk dibeli" → listing_type="sale"
- "apartemen kontrak bulanan" → listing_type="rent"
- "house for sale near USU" → listing_type="sale"
- "office space for rent" → listing_type="rent" """
    )
    source: Optional[str] = Field(
        default=None,
        description="Source type: 'project' for new developer properties (primary market), 'listing' for resale/secondary market. Leave empty to search both."
    )
    min_price: Optional[int] = Field(
        default=None,
        description="""Minimum price in IDR.

CRITICAL - Price pattern rules (NO tolerance, strict ranges):

1. 'harga X-an' pattern = "in the X range" (X to next tier - 1)
   MUST set BOTH min_price AND max_price:
   - 'harga 1M an' / '1 milyar-an' → min=1000000000, max=1999999999
   - 'harga 900jt an' → min=900000000, max=999999999
   - 'harga 800jt an' → min=800000000, max=899999999
   - 'harga 500jt an' → min=500000000, max=599999999
   - 'harga 200jt an' → min=200000000, max=299999999

2. 'diatas X' / 'minimal X' / 'mulai dari X':
   Only set min_price, NO max_price
   - 'diatas 1M' → min=1000000000, max=None

3. 'dibawah X' / 'maksimal X' / 'budget X':
   Only set max_price, NO min_price
   - 'dibawah 1M' → min=None, max=1000000000

WARNING: Do NOT apply ±10% or any tolerance to 'X-an' patterns!
'1M an' means EXACTLY 1B-1.99B, NOT 900jt-1.1B"""
    )
    max_price: Optional[int] = Field(
        default=None,
        description="""Maximum price in IDR.

CRITICAL - Must match min_price patterns:
- 'harga X-an' → set BOTH min AND max (see min_price for exact ranges)
- 'dibawah X' / 'maksimal X' / 'budget X' → only max_price=X, no min
- 'diatas X' / 'minimal X' → only min_price=X, no max

Examples:
- 'harga 1M an' → min=1000000000, max=1999999999 (NOT below 1B!)
- 'maksimal 800jt' → min=None, max=800000000
- 'budget 500jt' → min=None, max=500000000"""
    )
    min_bedrooms: Optional[int] = Field(
        default=None,
        description="""Minimum number of bedrooms. Use based on user's words:
- "3 kamar" (exact) → min_bedrooms=3, max_bedrooms=3
- "minimal 3 kamar" / "paling sedikit 3 kamar" → min_bedrooms=3, max_bedrooms=None
- "maksimal 3 kamar" / "paling banyak 3 kamar" → min_bedrooms=None, max_bedrooms=3"""
    )
    max_bedrooms: Optional[int] = Field(
        default=None,
        description="""Maximum number of bedrooms. Set equal to min_bedrooms for exact match.
- "3 kamar" (exact) → min_bedrooms=3, max_bedrooms=3
- "maksimal 3 kamar" → max_bedrooms=3"""
    )
    min_floors: Optional[int] = Field(
        default=None,
        description="""Minimum number of floors/stories. Use based on user's words:
- "3 lantai" / "3 tingkat" (exact) → min_floors=3, max_floors=3
- "minimal 3 lantai" / "paling sedikit 3 tingkat" → min_floors=3, max_floors=None
- "maksimal 3 lantai" → min_floors=None, max_floors=3"""
    )
    max_floors: Optional[int] = Field(
        default=None,
        description="""Maximum number of floors/stories. Set equal to min_floors for exact match.
- "3 lantai" (exact) → min_floors=3, max_floors=3
- "maksimal 3 lantai" → max_floors=3"""
    )
    amenities: Optional[List[str]] = Field(
        default=None,
        description="""List of required amenities/facilities. Include in query text for semantic search.

UNIT amenities: cctv, wifi, ac, garage, carport, furnished, semi_furnished, water_heater
COMPLEX/CLUSTER facilities: swimming_pool, security_24, basketball_court, tennis_court, jogging_track, playground, clubhouse, gym, taman

For complex facilities like "lapangan basket", "kolam renang", "jogging track":
- Add to amenities list AND include Indonesian term in query for better semantic matching
- Example: "komplek dengan lapangan basket" → amenities=['basketball_court'], query includes "lapangan basket" """
    )
    in_complex: Optional[bool] = Field(
        default=None,
        description="""Filter for properties in a complex/cluster or standalone.
- True: Only properties INSIDE a complex/cluster (has complex_name)
- False: Only STANDALONE properties (no complex_name)
- None (default): Show both

User keywords:
- "dalam komplek", "di komplek", "di cluster", "perumahan", "di kompleks" → in_complex=True
- "standalone", "bukan komplek", "berdiri sendiri", "di luar komplek" → in_complex=False"""
    )
    facing: Optional[str] = Field(
        default=None,
        description="""Property facing direction (hadap).
Values: 'utara' (north), 'selatan' (south), 'timur' (east), 'barat' (west),
        'timur_laut' (northeast), 'tenggara' (southeast), 'barat_daya' (southwest), 'barat_laut' (northwest)

User keywords:
- "hadap utara", "menghadap utara", "arah utara" → facing="utara"
- "hadap timur" → facing="timur"
- "hadap selatan" → facing="selatan"
- "hadap barat" → facing="barat" """
    )
    page: int = Field(
        default=1,
        description="""Page number for pagination. Default is 1 (first page).

Use page > 1 when user asks for MORE results with SAME criteria:
- "tampilkan lebih banyak" / "show more" → increment page
- "ada lagi?" / "any more?" → increment page
- "lanjutkan" / "next page" → increment page
- "pilihan lain" / "other options" → increment page

When using page > 1, you MUST use the SAME search parameters as the previous search."""
    )


class GetPropertyDetailInput(BaseModel):
    """Input schema for getting property details"""
    property_id: str = Field(
        description="The unique ID of the property to get details for"
    )


class GetPropertyByNumberInput(BaseModel):
    """Input schema for getting property by search result number"""
    number: int = Field(
        description="The result number from the last search (1-10). Use this when user says 'nomor 3', 'yang ke-5', etc."
    )


class SearchKnowledgeInput(BaseModel):
    """Input schema for knowledge base search"""
    query: str = Field(
        description="Question or topic to search in knowledge base"
    )
    category: Optional[str] = Field(
        default=None,
        description="Knowledge category: 'sales-techniques', 'real-estate-knowledge', 'motivational'"
    )


class GeocodeLocationInput(BaseModel):
    """Input schema for geocoding a location - Global support"""
    location_name: str = Field(
        description="""Name of the location, landmark, or address to geocode.

Examples (Global):
- "Orchard Road" (Singapore)
- "Central Park" (New York)
- "Kemang" (Jakarta)
- "Ringroad" (Medan)
"""
    )
    city: Optional[str] = Field(
        default=None,
        description="City context for better geocoding accuracy. Examples: 'Jakarta', 'Singapore', 'New York'"
    )
    country: str = Field(
        default="Indonesia",
        description="Country context. Examples: 'Indonesia', 'Singapore', 'USA', 'Malaysia'"
    )


class SearchNearbyInput(BaseModel):
    """Input schema for searching properties near a landmark - Global support with full filters"""
    location_name: str = Field(
        description="""Name of the landmark or POI to search near.

Use this for proximity searches with words like "dekat", "near", "sekitar".

Examples (Global):
- "house near Central Park" → location_name="Central Park"
- "rumah dekat USU" → location_name="USU"
- "apartment near Orchard MRT" → location_name="Orchard MRT"
- "rumah sekitar Sun Plaza" → location_name="Sun Plaza"
"""
    )
    city: Optional[str] = Field(
        default=None,
        description="City context for geocoding. Examples: 'Jakarta', 'Medan', 'Singapore', 'New York'"
    )
    country: str = Field(
        default="Indonesia",
        description="Country context. Examples: 'Indonesia', 'Singapore', 'USA'"
    )
    radius_km: float = Field(
        default=3.0,
        description="""Search radius in kilometers:
- 'dekat'/'near' → 1km
- 'sekitar'/'around' → 2km
- 'kawasan'/'area' → 3km (default)
- User specified radius → use that value"""
    )
    query: Optional[str] = Field(
        default=None,
        description="Text search for features/amenities (separate from location)"
    )
    property_type: Optional[str] = Field(
        default=None,
        description="Type of property: 'house', 'shophouse', 'land', 'apartment', 'warehouse'"
    )
    listing_type: Optional[str] = Field(
        default=None,
        description="""Listing type: 'sale' or 'rent'.
- SALE: "dijual", "for sale", "buy"
- RENT: "disewa", "for rent", "sewa" """
    )
    source: Optional[str] = Field(
        default=None,
        description="Source: 'project' (new development) or 'listing' (resale). Empty for both."
    )
    min_price: Optional[int] = Field(
        default=None,
        description="Minimum price. For 'X-an' pattern: set both min AND max (e.g., '1M an' → min=1B, max=1.99B)"
    )
    max_price: Optional[int] = Field(
        default=None,
        description="Maximum price. For 'X-an' pattern: set both min AND max. For 'dibawah X': only set max"
    )
    min_bedrooms: Optional[int] = Field(
        default=None,
        description="Minimum number of bedrooms"
    )
    max_bedrooms: Optional[int] = Field(
        default=None,
        description="Maximum number of bedrooms"
    )
    min_floors: Optional[int] = Field(
        default=None,
        description="Minimum number of floors"
    )
    max_floors: Optional[int] = Field(
        default=None,
        description="Maximum number of floors"
    )
    amenities: Optional[List[str]] = Field(
        default=None,
        description="Required amenities: cctv, wifi, pool, gym, etc."
    )
    in_complex: Optional[bool] = Field(
        default=None,
        description="True=in complex, False=standalone, None=both"
    )
    facing: Optional[str] = Field(
        default=None,
        description="Facing direction: 'utara', 'selatan', 'timur', 'barat'"
    )
    page: int = Field(
        default=1,
        description="Page number for pagination"
    )


class SearchPOIsInput(BaseModel):
    """Input schema for searching Points of Interest (POIs) - Global support"""
    poi_type: str = Field(
        description="""Type of POI to search:
- 'school' / 'sekolah'
- 'mall' / 'pusat perbelanjaan'
- 'hospital' / 'rumah sakit'
- 'university' / 'universitas'
"""
    )
    city: str = Field(
        description="""REQUIRED. City to search POIs in.
Examples: 'Jakarta', 'Medan', 'Singapore', 'New York', 'Kuala Lumpur'
"""
    )
    country: str = Field(
        default="Indonesia",
        description="Country context. Examples: 'Indonesia', 'Singapore', 'USA', 'Malaysia'"
    )
    limit: int = Field(
        default=5,
        description="Maximum number of POIs to return. Default is 5."
    )


class SearchPropertiesByLocationInput(BaseModel):
    """Input schema for location-based property search - Global support"""
    location_keyword: str = Field(
        description="""REQUIRED. The location/area extracted from user query.
This will be geocoded to get coordinates for the search.

Examples (Indonesian):
- "rumah di ringroad" → location_keyword="ringroad"
- "apartemen di Kemang" → location_keyword="Kemang"
- "rumah daerah BSD" → location_keyword="BSD"

Examples (English):
- "house in Brooklyn" → location_keyword="Brooklyn"
- "apartment in Orchard" → location_keyword="Orchard"
- "property in Bangsar" → location_keyword="Bangsar"
"""
    )
    city: Optional[str] = Field(
        default=None,
        description="""City context for better geocoding accuracy.
Examples: 'Jakarta', 'Medan', 'Singapore', 'New York', 'Kuala Lumpur'
Extract from user query if mentioned."""
    )
    country: str = Field(
        default="Indonesia",
        description="Country context. Examples: 'Indonesia', 'Singapore', 'USA', 'Malaysia'"
    )
    radius_km: float = Field(
        default=3.0,
        description="""Search radius in kilometers from the geocoded location.
- Urban district: 2-3km
- Specific area: 3km (default)
- Large suburban area: 5km"""
    )
    query: Optional[str] = Field(
        default=None,
        description="""Optional text search for features/amenities (SEPARATE from location).
Location is handled by location_keyword, this is for additional filters.

Examples:
- "rumah furnished di ringroad" → query="furnished"
- "house with pool in Brooklyn" → query="pool"
"""
    )
    property_type: Optional[str] = Field(
        default=None,
        description="Type: 'house', 'shophouse', 'land', 'apartment', 'warehouse'"
    )
    listing_type: Optional[str] = Field(
        default=None,
        description="Listing: 'sale' or 'rent'"
    )
    source: Optional[str] = Field(
        default=None,
        description="Source: 'project' (new) or 'listing' (resale)"
    )
    min_price: Optional[int] = Field(
        default=None,
        description="Minimum price. For 'X-an' pattern: set both min AND max (e.g., '1M an' → min=1B, max=1.99B)"
    )
    max_price: Optional[int] = Field(
        default=None,
        description="Maximum price. For 'X-an' pattern: set both min AND max. For 'dibawah X': only set max"
    )
    min_bedrooms: Optional[int] = Field(
        default=None,
        description="Minimum bedrooms"
    )
    max_bedrooms: Optional[int] = Field(
        default=None,
        description="Maximum bedrooms"
    )
    min_floors: Optional[int] = Field(
        default=None,
        description="Minimum floors"
    )
    max_floors: Optional[int] = Field(
        default=None,
        description="Maximum floors"
    )
    amenities: Optional[List[str]] = Field(
        default=None,
        description="Required amenities: cctv, wifi, pool, gym, etc."
    )
    in_complex: Optional[bool] = Field(
        default=None,
        description="True=in complex, False=standalone, None=both"
    )
    facing: Optional[str] = Field(
        default=None,
        description="Facing direction: 'north', 'south', 'east', 'west'"
    )
    page: int = Field(
        default=1,
        description="Page number for pagination"
    )


# ============================================================================
# Tool Factory - Creates tools with injected dependencies
# ============================================================================

# User-scoped cache for search results to prevent cross-user data leakage
# Format: {user_id: {result_number: Property}}
_user_search_results: dict[str, dict[int, "Property"]] = {}

# Current user context (set by agent before tool execution)
from contextvars import ContextVar
_current_user_id: ContextVar[str] = ContextVar("current_user_id", default="anonymous")


def set_current_user(user_id: str) -> None:
    """Set the current user context for tool cache isolation."""
    _current_user_id.set(user_id)


def get_current_user() -> str:
    """Get the current user from context."""
    return _current_user_id.get()


def get_user_search_results(user_id: str = None) -> dict[int, "Property"]:
    """Get search results for a specific user."""
    uid = user_id or get_current_user()
    return _user_search_results.get(uid, {})


def set_user_search_results(results: dict[int, "Property"], user_id: str = None) -> None:
    """Set search results for a specific user."""
    uid = user_id or get_current_user()
    _user_search_results[uid] = results


def clear_user_search_results(user_id: str = None) -> None:
    """Clear search results for a specific user."""
    uid = user_id or get_current_user()
    if uid in _user_search_results:
        del _user_search_results[uid]


# User-scoped cache for last search state (criteria + pagination info)
# Format: {user_id: {"criteria": SearchCriteria, "page": int, "total": int, "has_more": bool}}
_user_search_state: dict[str, dict] = {}


def get_user_search_state(user_id: str = None) -> Optional[dict]:
    """Get last search state for a specific user (for follow-up/pagination)."""
    uid = user_id or get_current_user()
    return _user_search_state.get(uid)


def set_user_search_state(
    criteria: SearchCriteria,
    page: int,
    total: int,
    has_more: bool,
    user_id: str = None
) -> None:
    """Store search state for a specific user (for follow-up/pagination)."""
    uid = user_id or get_current_user()
    _user_search_state[uid] = {
        "criteria": criteria,
        "page": page,
        "total": total,
        "has_more": has_more,
    }


def clear_user_search_state(user_id: str = None) -> None:
    """Clear search state for a specific user."""
    uid = user_id or get_current_user()
    if uid in _user_search_state:
        del _user_search_state[uid]


# Legacy aliases for backward compatibility
def get_user_search_criteria(user_id: str = None) -> Optional[SearchCriteria]:
    """Get last search criteria for a specific user (for follow-up queries)."""
    state = get_user_search_state(user_id)
    return state.get("criteria") if state else None


def set_user_search_criteria(criteria: SearchCriteria, user_id: str = None) -> None:
    """Store search criteria for a specific user (legacy - use set_user_search_state)."""
    set_user_search_state(criteria, page=1, total=0, has_more=False, user_id=user_id)


def clear_user_search_criteria(user_id: str = None) -> None:
    """Clear search criteria for a specific user."""
    clear_user_search_state(user_id)


def create_property_tools(
    adapter: PropertyDataAdapter,
    vector_store: Optional[Chroma] = None,
    property_store: Optional[PropertyStore] = None,
    use_hybrid_search: bool = True,
) -> list:
    """
    Factory function to create property-related tools with injected dependencies.
    
    Args:
        adapter: PropertyDataAdapter for API/data access
        vector_store: Optional Chroma vector store for knowledge search
        property_store: Optional PropertyStore for hybrid semantic search
        use_hybrid_search: Enable hybrid search (API + ChromaDB re-ranking)
        
    Returns:
        List of LangChain tools
    """
    # Using user-scoped cache (no global needed)
    
    # Initialize hybrid search service if property_store provided
    hybrid_service = None
    if use_hybrid_search and property_store:
        hybrid_service = HybridSearchService(
            property_store=property_store,
            semantic_weight=0.6,  # 60% semantic, 40% API order
        )
    
    # Helper function for geocoding (shared by all location-based tools)
    def _geocode(
        location_name: str,
        city: Optional[str] = None,
        country: str = "Indonesia"
    ) -> Optional[dict]:
        """
        Geocode a location using Google Maps API (preferred) or Nominatim (fallback).
        Global support - no hardcoded city defaults.

        Args:
            location_name: Location/landmark/address to geocode
            city: Optional city context for better accuracy
            country: Country context (default Indonesia)

        Returns:
            dict with lat, lng, display_name or None if not found
        """
        import httpx

        google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

        # Build search query with context
        parts = [location_name]
        if city:
            parts.append(city)
        parts.append(country)
        search_query = ", ".join(parts)

        if google_api_key:
            # Use Google Maps Geocoding API
            geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                "address": search_query,
                "key": google_api_key,
            }

            try:
                response = httpx.get(geocode_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "OK" and data.get("results"):
                        result = data["results"][0]
                        location = result.get("geometry", {}).get("location", {})
                        return {
                            "lat": location.get("lat", 0),
                            "lng": location.get("lng", 0),
                            "display_name": result.get("formatted_address", location_name),
                        }
                    elif data.get("status") == "ZERO_RESULTS":
                        return None
            except Exception as e:
                logger.warning("google_geocode_failed", error=str(e))

        # Fallback to Nominatim (free, no API key)
        headers = {"User-Agent": "PropertySearchBot/1.0"}

        try:
            response = httpx.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": search_query,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                },
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if data:
                result = data[0]
                return {
                    "lat": float(result["lat"]),
                    "lng": float(result["lon"]),
                    "display_name": result.get("display_name", location_name),
                }
        except Exception as e:
            logger.warning("nominatim_geocode_failed", error=str(e))

        return None

    @tool(args_schema=SearchPropertiesInput)
    def search_properties(
        user_query: str,
        query: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        source: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_bedrooms: Optional[int] = None,
        max_bedrooms: Optional[int] = None,
        min_floors: Optional[int] = None,
        max_floors: Optional[int] = None,
        amenities: Optional[List[str]] = None,
        in_complex: Optional[bool] = None,
        facing: Optional[str] = None,
        page: int = 1,
    ) -> str:
        """
        Search properties by filters and text - NO specific location.
        For location-based search, use search_properties_by_location instead.

        Use this for:
        - Filter by price, bedrooms, property type
        - Text search for features/amenities
        - General queries WITHOUT specific location

        DO NOT use for location queries like "di ringroad", "in Brooklyn".
        Use search_properties_by_location for those.

        Examples:
        - "rumah murah 3 kamar" → min_bedrooms=3, max_bedrooms=3
        - "apartemen furnished" → query="furnished", property_type="apartment"
        - "ruko dijual" → property_type="shophouse", listing_type="sale"
        - "house with pool" → query="pool", property_type="house"
        """
        # Initialize tool metrics
        tool_metrics = ToolMetrics(
            tool_name="search_properties",
            tool_args={
                "user_query": user_query,
                "query": query,
                "property_type": property_type,
                "listing_type": listing_type,
                "source": source,
                "min_price": min_price,
                "max_price": max_price,
                "min_bedrooms": min_bedrooms,
                "max_bedrooms": max_bedrooms,
                "min_floors": min_floors,
                "max_floors": max_floors,
                "amenities": amenities,
                "in_complex": in_complex,
                "facing": facing,
                "page": page,
            },
            user_id=get_current_user(),
        )
        timer = Timer()

        with timer:
          try:
            # Use query as-is for text search (no location expansion needed)
            search_query = query or ""

            # Build search criteria
            current_criteria = SearchCriteria(
                query=search_query,
                property_type=PropertyType(property_type) if property_type else None,
                listing_type=ListingType(listing_type) if listing_type else None,
                source=source,
                min_price=min_price,
                max_price=max_price,
                min_bedrooms=min_bedrooms,
                max_bedrooms=max_bedrooms,
                min_floors=min_floors,
                max_floors=max_floors,
                page=page,
                limit=10,
            )

            # Use Hybrid Search if available
            if hybrid_service:
                result = run_async(hybrid_service.search(
                    adapter=adapter,
                    query=search_query,
                    user_query=user_query,  # Original user message for semantic search
                    property_type=property_type,
                    listing_type=listing_type,
                    source=source,
                    min_price=min_price,
                    max_price=max_price,
                    min_bedrooms=min_bedrooms,
                    max_bedrooms=max_bedrooms,
                    min_floors=min_floors,
                    max_floors=max_floors,
                    amenities=amenities,
                    in_complex=in_complex,
                    facing=facing,
                    page=page,
                    limit=10,
                    use_semantic_rerank=True,
                ))

                properties = result.properties
                total = result.total
                has_more = result.has_more
                is_hybrid = result.reranked
                semantic_scores = result.semantic_scores
            else:
                # Fallback to API-only search
                api_result = run_async(adapter.search(current_criteria))
                properties = api_result.properties
                total = api_result.total
                has_more = api_result.has_more
                is_hybrid = False
                semantic_scores = {}

            # Store search state for pagination/follow-up
            set_user_search_state(
                criteria=current_criteria,
                page=page,
                total=total,
                has_more=has_more,
            )
            
            if not properties:
                clear_user_search_results()
                clear_user_search_state()
                if page > 1:
                    return f"Tidak ada lagi properti di halaman {page}. Semua hasil sudah ditampilkan."
                return f"Tidak ditemukan properti dengan kriteria pencarian '{query}'. Coba perluas area pencarian atau ubah filter."

            # Cache results for later reference by number (user-scoped)
            results_cache = {}
            for i, prop in enumerate(properties[:10], 1):
                results_cache[i] = prop
            set_user_search_results(results_cache)
            
            # Format results
            search_type = "🔀 Hybrid" if is_hybrid else "📡 API"
            start_idx = (page - 1) * 10 + 1
            end_idx = min(page * 10, total)
            page_info = f"(Halaman {page}, menampilkan {start_idx}-{end_idx} dari {total})" if total > 10 else ""
            output_lines = [f"Ditemukan {total} properti ({search_type}) {page_info}:"]
            
            for i, prop in enumerate(properties[:10], 1):
                price_str = f"Rp {prop.price:,.0f}".replace(",", ".")
                features = []
                if prop.bedrooms:
                    features.append(f"{prop.bedrooms} KT")
                if prop.bathrooms:
                    features.append(f"{prop.bathrooms} KM")
                if prop.land_area:
                    features.append(f"LT {prop.land_area}m²")
                if prop.building_area:
                    features.append(f"LB {prop.building_area}m²")
                    
                features_str = ", ".join(features) if features else ""
                
                # Source type indicator
                if prop.source_type == "project":
                    source_label = "🏗️ Proyek Baru"
                else:
                    source_label = "🔄 Resale"
                developer_info = f" by {prop.developer_name}" if prop.developer_name else ""
                
                # Semantic relevance score (if available)
                sem_score = semantic_scores.get(str(prop.id), 0)
                relevance = f" [relevance: {sem_score:.2f}]" if sem_score > 0 else ""
                
                # URL from API
                url_line = f"\n   🔗 {prop.url_view}" if prop.url_view else ""
                
                # Debug info: lat/long
                coords = ""
                if prop.latitude and prop.longitude:
                    try:
                        lat_f = float(prop.latitude)
                        lng_f = float(prop.longitude)
                        coords = f"\n   🌐 Koordinat: {lat_f:.6f}, {lng_f:.6f}"
                    except (ValueError, TypeError):
                        coords = f"\n   🌐 Koordinat: {prop.latitude}, {prop.longitude}"
                
                output_lines.append(
                    f"\n{i}. **{prop.title}**{relevance}\n"
                    f"   {source_label}{developer_info}{url_line}\n"
                    f"   📍 {prop.address or ''}, {prop.location or ''}, {prop.city or ''}{coords}\n"
                    f"   💰 {price_str} ({prop.listing_type})\n"
                    f"   🏠 {features_str}"
                )
            
            # Show pagination hint if there are more results
            if has_more:
                remaining = total - (page * 10)
                if remaining > 0:
                    output_lines.append(f"\n📄 Masih ada {remaining} properti lagi. Ketik 'tampilkan lebih banyak' atau 'lanjutkan' untuk melihat halaman berikutnya.")
            
            result = "\n".join(output_lines)
            
            # Log successful tool metrics
            tool_metrics.success = True
            tool_metrics.result_count = len(properties[:10])
            tool_metrics.result_size_chars = len(result)
            tool_metrics.latency_ms = timer.elapsed_ms
            get_metrics_collector().log_tool(tool_metrics)
                
            return result
            
          except Exception as e:
            # Log failed tool metrics
            tool_metrics.success = False
            tool_metrics.error_message = str(e)
            tool_metrics.latency_ms = timer.elapsed_ms
            get_metrics_collector().log_tool(tool_metrics)
            return f"Error searching properties: {str(e)}"
    
    @tool(args_schema=GetPropertyDetailInput)
    def get_property_detail(property_id: str) -> str:
        """
        Get detailed information about a specific property by its ID.
        
        Use this when:
        - User asks for more details about a specific property
        - User refers to a property by ID
        - Need complete property information for update or description
        """
        tool_metrics = ToolMetrics(
            tool_name="get_property_detail",
            tool_args={"property_id": property_id},
            user_id=get_current_user(),
        )
        timer = Timer()
        
        with timer:
          try:
            prop = run_async(adapter.get_by_id(property_id))
            
            if not prop:
                tool_metrics.success = True
                tool_metrics.result_count = 0
                tool_metrics.latency_ms = timer.elapsed_ms
                get_metrics_collector().log_tool(tool_metrics)
                return f"Property with ID {property_id} not found."
            
            # Format detailed property info
            details = [
                f"# {prop.title}",
                f"\n**ID:** {prop.id}",
                f"**Type:** {prop.property_type} ({prop.listing_type})",
                f"**Price:** Rp {prop.price:,.0f}".replace(",", "."),
                f"\n**Location:**",
                f"  - Address: {prop.address or 'N/A'}",
                f"  - Area: {prop.location or 'N/A'}",
                f"  - City: {prop.city or 'N/A'}",
                f"\n**Specifications:**",
                f"  - Bedrooms: {prop.bedrooms or 'N/A'}",
                f"  - Bathrooms: {prop.bathrooms or 'N/A'}",
                f"  - Land Area: {prop.land_area or 'N/A'} m²",
                f"  - Building Area: {prop.building_area or 'N/A'} m²",
            ]
            
            if prop.description:
                details.append(f"\n**Description:**\n{prop.description}")
                
            if prop.features:
                details.append(f"\n**Features:** {', '.join(prop.features)}")
            
            result = "\n".join(details)
            
            tool_metrics.success = True
            tool_metrics.result_count = 1
            tool_metrics.result_size_chars = len(result)
            tool_metrics.latency_ms = timer.elapsed_ms
            get_metrics_collector().log_tool(tool_metrics)
            
            return result
            
          except Exception as e:
            tool_metrics.success = False
            tool_metrics.error_message = str(e)
            tool_metrics.latency_ms = timer.elapsed_ms
            get_metrics_collector().log_tool(tool_metrics)
            return f"Error getting property details: {str(e)}"
    
    @tool(args_schema=GetPropertyByNumberInput)
    def get_property_by_number(number: int) -> str:
        """
        Get detailed information about a property from the last search results by its number.
        
        Use this when:
        - User refers to a property by number from search results (e.g., "nomor 3", "yang ke-5", "detail no 8")
        - User wants more info about a specific result without mentioning the ID
        
        Examples:
        - "detail nomor 3" -> number=3
        - "yang ke-5 gimana?" -> number=5
        - "info lebih lanjut untuk no 8" -> number=8
        """
        # Get user-scoped search results
        user_results = get_user_search_results()

        if not user_results:
            return "Tidak ada hasil pencarian sebelumnya. Silakan lakukan pencarian terlebih dahulu."

        if number < 1 or number > len(user_results):
            available = list(user_results.keys())
            return f"Nomor {number} tidak valid. Pilihan yang tersedia: {min(available)} sampai {max(available)}"

        prop = user_results.get(number)
        if not prop:
            return f"Properti nomor {number} tidak ditemukan dalam hasil pencarian terakhir."
        
        # Format detailed property info (same as get_property_detail)
        details = [
            f"# {prop.title}",
            f"\n**ID:** {prop.id}",
            f"**Source:** {'🏗️ Proyek Baru' if prop.source_type == 'project' else '🔄 Resale'}",
        ]
        
        if prop.url_view:
            details.append(f"**URL:** {prop.url_view}")
        
        details.extend([
            f"**Type:** {prop.property_type} ({prop.listing_type})",
            f"**Price:** Rp {prop.price:,.0f}".replace(",", "."),
            f"\n**Location:**",
            f"- Address: {prop.address or 'N/A'}",
            f"- Area: {prop.location}",
            f"- City: {prop.city}",
        ])
        
        if prop.latitude and prop.longitude:
            try:
                lat_f = float(prop.latitude)
                lng_f = float(prop.longitude)
                details.append(f"- Coordinates: {lat_f:.6f}, {lng_f:.6f}")
            except (ValueError, TypeError):
                details.append(f"- Coordinates: {prop.latitude}, {prop.longitude}")
        
        details.append(f"\n**Specifications:**")
        if prop.bedrooms:
            details.append(f"- Bedrooms: {prop.bedrooms}")
        if prop.bathrooms:
            details.append(f"- Bathrooms: {prop.bathrooms}")
        if prop.land_area:
            details.append(f"- Land Area: {prop.land_area} m²")
        if prop.building_area:
            details.append(f"- Building Area: {prop.building_area} m²")
        if prop.floors:
            details.append(f"- Floors: {prop.floors}")
        if prop.certificate_type:
            details.append(f"- Certificate: {prop.certificate_type}")
        
        if prop.description:
            details.append(f"\n**Description:**\n{prop.description[:500]}...")
        
        if prop.features:
            details.append(f"\n**Features:** {', '.join(prop.features[:10])}")
        
        if prop.agent:
            details.append(f"\n**Contact:**")
            details.append(f"- Agent: {prop.agent.name}")
            if prop.agent.phone:
                details.append(f"- Phone: {prop.agent.phone}")
        
        if prop.developer_name:
            details.append(f"- Developer: {prop.developer_name}")
        
        return "\n".join(details)
    
    @tool(args_schema=GeocodeLocationInput)
    def geocode_location(
        location_name: str,
        city: Optional[str] = None,
        country: str = "Indonesia",
    ) -> str:
        """
        Convert a location name to coordinates (lat/lng). Global support.

        Examples:
        - "Orchard Road", city="Singapore", country="Singapore"
        - "Central Park", city="New York", country="USA"
        - "Kemang", city="Jakarta", country="Indonesia"
        """
        try:
            result = _geocode(location_name, city=city, country=country)

            if not result:
                return f"Location '{location_name}' not found. Try with more specific name or add city context."

            return f"""Coordinates for "{location_name}":
- Latitude: {result['lat']}
- Longitude: {result['lng']}
- Full address: {result['display_name']}

Use these coordinates with search_nearby or search_properties_by_location."""

        except Exception as e:
            return f"Error geocoding location: {str(e)}"
    
    @tool(args_schema=SearchNearbyInput)
    def search_nearby(
        location_name: str,
        city: Optional[str] = None,
        country: str = "Indonesia",
        radius_km: float = 3.0,
        query: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        source: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_bedrooms: Optional[int] = None,
        max_bedrooms: Optional[int] = None,
        min_floors: Optional[int] = None,
        max_floors: Optional[int] = None,
        amenities: Optional[List[str]] = None,
        in_complex: Optional[bool] = None,
        facing: Optional[str] = None,
        page: int = 1,
    ) -> str:
        """
        Search properties near a landmark/POI. Global support with full filters.
        Use for proximity queries with "dekat", "near", "sekitar".

        Radius guidelines:
        - "dekat"/"near" → 1km
        - "sekitar"/"around" → 2km
        - "kawasan"/"area" → 3km

        Examples (Global):
        - "rumah 3 kamar dekat USU" → location_name="USU", city="Medan", min_bedrooms=3, max_bedrooms=3
        - "house near Central Park" → location_name="Central Park", city="New York", country="USA"
        - "apartment near Orchard MRT" → location_name="Orchard MRT", city="Singapore", country="Singapore"
        """
        try:
            # Step 1: Geocode the location
            geo_result = _geocode(location_name, city=city, country=country)

            if not geo_result:
                return f"Lokasi '{location_name}' tidak ditemukan. Coba dengan nama yang lebih spesifik atau gunakan search_properties dengan kata kunci."

            lat = geo_result["lat"]
            lng = geo_result["lng"]

            # Step 2: Search properties with coordinates and all filters
            criteria = SearchCriteria(
                query=query,
                latitude=lat,
                longitude=lng,
                radius_km=radius_km,
                property_type=PropertyType(property_type) if property_type else None,
                listing_type=ListingType(listing_type) if listing_type else None,
                source=source,
                min_price=min_price,
                max_price=max_price,
                min_bedrooms=min_bedrooms,
                max_bedrooms=max_bedrooms,
                min_floors=min_floors,
                max_floors=max_floors,
                page=page,
                limit=10,
            )

            # Use Hybrid Search if available for better results
            if hybrid_service:
                result = run_async(hybrid_service.search(
                    adapter=adapter,
                    query=query or location_name,
                    property_type=property_type,
                    listing_type=listing_type,
                    source=source,
                    min_price=min_price,
                    max_price=max_price,
                    min_bedrooms=min_bedrooms,
                    max_bedrooms=max_bedrooms,
                    min_floors=min_floors,
                    max_floors=max_floors,
                    amenities=amenities,
                    in_complex=in_complex,
                    facing=facing,
                    latitude=lat,
                    longitude=lng,
                    radius_km=radius_km,
                    page=page,
                    limit=10,
                    use_semantic_rerank=True,
                    skip_chromadb_fallback=True,  # Don't fallback to ChromaDB when API empty
                ))
                properties = result.properties
                total = result.total
                has_more = result.has_more
            else:
                api_result = run_async(adapter.search(criteria))
                properties = api_result.properties
                total = api_result.total
                has_more = api_result.has_more

            if not properties:
                clear_user_search_results()
                if page > 1:
                    return f"Tidak ada lagi properti di halaman {page}."
                return f"Tidak ditemukan properti dalam radius {radius_km}km dari {location_name} (koordinat: {lat:.4f}, {lng:.4f}). Coba perbesar radius atau ubah filter."

            # Sort by distance (closest first)
            properties_sorted = sorted(
                properties,
                key=lambda p: p.distance_km if p.distance_km is not None else float('inf')
            )

            # Cache results for later reference by number (user-scoped)
            results_cache = {}
            for i, prop in enumerate(properties_sorted[:10], 1):
                results_cache[i] = prop
            set_user_search_results(results_cache)

            # Store search state for pagination
            set_user_search_state(
                criteria=criteria,
                page=page,
                total=total,
                has_more=has_more,
            )

            # Format results with distance info
            start_idx = (page - 1) * 10 + 1
            end_idx = min(page * 10, total)
            page_info = f"(Halaman {page}, {start_idx}-{end_idx} dari {total})" if total > 10 else ""

            output_lines = [
                f"Ditemukan {total} properti dalam radius {radius_km}km dari {location_name} {page_info}:",
                f"(Koordinat pusat: {lat:.6f}, {lng:.6f})",
                f"(Diurutkan dari yang terdekat)"
            ]

            for i, prop in enumerate(properties_sorted[:10], 1):
                price_str = f"Rp {prop.price:,.0f}".replace(",", ".")
                features = []
                if prop.bedrooms:
                    features.append(f"{prop.bedrooms} KT")
                if prop.bathrooms:
                    features.append(f"{prop.bathrooms} KM")
                if prop.land_area:
                    features.append(f"LT {prop.land_area}m²")

                features_str = ", ".join(features) if features else ""

                # Source type indicator
                if prop.source_type == "project":
                    source_label = "🏗️ Proyek Baru"
                else:
                    source_label = "🔄 Resale"
                developer_info = f" by {prop.developer_name}" if prop.developer_name else ""

                # Distance info
                distance_str = ""
                if prop.distance_km is not None:
                    if prop.distance_km < 1:
                        distance_str = f"📏 {prop.distance_km * 1000:.0f}m"
                    else:
                        distance_str = f"📏 {prop.distance_km:.1f}km"

                # URL from API
                url_line = f"\n   🔗 {prop.url_view}" if prop.url_view else ""

                output_lines.append(
                    f"\n{i}. **{prop.title}** {distance_str}\n"
                    f"   {source_label}{developer_info}{url_line}\n"
                    f"   📍 {prop.address or ''}, {prop.location or ''}\n"
                    f"   💰 {price_str} ({prop.listing_type})\n"
                    f"   🏠 {features_str}"
                )

            if has_more:
                remaining = total - (page * 10)
                if remaining > 0:
                    output_lines.append(f"\n📄 Masih ada {remaining} properti lagi. Ketik 'tampilkan lebih banyak' untuk halaman berikutnya.")

            return "\n".join(output_lines)

        except Exception as e:
            return f"Error searching nearby properties: {str(e)}"

    @tool(args_schema=SearchPOIsInput)
    def search_pois(
        poi_type: str,
        city: str,
        country: str = "Indonesia",
        limit: int = 5,
    ) -> str:
        """
        Search for POIs (schools, malls, hospitals) in a city. Global support.

        Use this FIRST when user asks for properties near a generic POI type.
        Then use search_nearby with specific POI names from results.

        Examples (Global):
        - search_pois(poi_type="school", city="Jakarta")
        - search_pois(poi_type="mall", city="Singapore", country="Singapore")
        - search_pois(poi_type="hospital", city="New York", country="USA")
        """
        import httpx

        try:
            poi_type_lower = poi_type.lower().strip()

            # Normalize POI type
            if poi_type_lower in ["sekolah"]:
                poi_type_lower = "school"
            elif poi_type_lower in ["pusat perbelanjaan"]:
                poi_type_lower = "mall"
            elif poi_type_lower in ["rumah sakit"]:
                poi_type_lower = "hospital"
            elif poi_type_lower in ["universitas", "kampus"]:
                poi_type_lower = "university"

            poi_type_display = {
                "school": "Sekolah",
                "mall": "Mall/Pusat Perbelanjaan",
                "hospital": "Rumah Sakit",
                "university": "Universitas",
            }.get(poi_type_lower, poi_type)

            pois = []

            # Always use Google Maps Places API for all cities
            google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

            if not google_api_key:
                return f"Google Maps API key tidak dikonfigurasi. Silakan set GOOGLE_MAPS_API_KEY di environment variables."

            # Build search query in Indonesian
            query_map = {
                "school": "sekolah",
                "mall": "mall",
                "hospital": "rumah sakit",
                "university": "universitas",
            }
            search_query = query_map.get(poi_type_lower, poi_type_lower)

            # Google Maps Places Text Search API
            places_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            # Build query with city and country context
            search_location = f"{city}, {country}" if country != "Indonesia" else city
            params = {
                "query": f"{search_query} in {search_location}",
                "key": google_api_key,
            }

            response = httpx.get(places_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "OK":
                    for place in data.get("results", [])[:limit]:
                        location = place.get("geometry", {}).get("location", {})
                        # Extract area from formatted_address
                        address = place.get("formatted_address", "")
                        # Try to get suburb/district from address parts
                        address_parts = address.split(",")
                        area = address_parts[1].strip() if len(address_parts) > 1 else city

                        pois.append({
                            "name": place.get("name", "Unknown"),
                            "lat": location.get("lat", 0),
                            "lng": location.get("lng", 0),
                            "area": area,
                        })
                elif data.get("status") == "ZERO_RESULTS":
                    pass  # pois remains empty
                else:
                    return f"Google Maps API error: {data.get('status')}. Error message: {data.get('error_message', 'Unknown error')}"

            if not pois:
                return f"Tidak ditemukan {poi_type_display} di {city}. Coba gunakan nama kota yang lebih spesifik atau cari di kota lain."

            # Format output
            output_lines = [
                f"Ditemukan {len(pois[:limit])} {poi_type_display} di {city}:",
                "",
                "Gunakan nama-nama ini dengan search_nearby untuk mencari properti di sekitarnya:",
                ""
            ]

            for i, poi in enumerate(pois[:limit], 1):
                output_lines.append(
                    f"{i}. **{poi['name']}**\n"
                    f"   📍 Area: {poi['area']}\n"
                    f"   📌 Koordinat: {poi['lat']:.4f}, {poi['lng']:.4f}"
                )

            output_lines.append("")
            output_lines.append("**Contoh penggunaan:**")
            if pois:
                first_poi = pois[0]['name']
                output_lines.append(f"- search_nearby(location_name=\"{first_poi}\", radius_km=2)")

            return "\n".join(output_lines)

        except Exception as e:
            return f"Error searching POIs: {str(e)}"

    @tool(args_schema=SearchPropertiesByLocationInput)
    def search_properties_by_location(
        location_keyword: str,
        city: Optional[str] = None,
        country: str = "Indonesia",
        radius_km: float = 3.0,
        query: Optional[str] = None,
        property_type: Optional[str] = None,
        listing_type: Optional[str] = None,
        source: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_bedrooms: Optional[int] = None,
        max_bedrooms: Optional[int] = None,
        min_floors: Optional[int] = None,
        max_floors: Optional[int] = None,
        amenities: Optional[List[str]] = None,
        in_complex: Optional[bool] = None,
        facing: Optional[str] = None,
        page: int = 1,
    ) -> str:
        """
        Search properties in a specific location/area. Global support.
        This tool geocodes the location first, then searches within radius.

        Use for location queries like "di [area]", "in [area]", "daerah [area]".
        DO NOT use for proximity queries (use search_nearby instead).

        Examples (Indonesian):
        - "rumah di ringroad" → location_keyword="ringroad", city="Medan"
        - "apartemen di BSD" → location_keyword="BSD", city="Tangerang"
        - "rumah furnished di Kemang" → location_keyword="Kemang", query="furnished", city="Jakarta"

        Examples (English):
        - "house in Brooklyn" → location_keyword="Brooklyn", city="New York", country="USA"
        - "apartment in Orchard" → location_keyword="Orchard", city="Singapore", country="Singapore"
        """
        # Initialize tool metrics
        tool_metrics = ToolMetrics(
            tool_name="search_properties_by_location",
            tool_args={
                "location_keyword": location_keyword,
                "city": city,
                "country": country,
                "radius_km": radius_km,
                "query": query,
                "property_type": property_type,
                "listing_type": listing_type,
                "source": source,
                "min_price": min_price,
                "max_price": max_price,
                "min_bedrooms": min_bedrooms,
                "max_bedrooms": max_bedrooms,
                "page": page,
            },
            user_id=get_current_user(),
        )
        timer = Timer()

        with timer:
          try:
            # Step 1: Geocode the location
            geo_result = _geocode(location_keyword, city=city, country=country)

            if not geo_result:
                return f"Location '{location_keyword}' not found. Try adding city context or use a more specific name."

            lat = geo_result["lat"]
            lng = geo_result["lng"]
            display_name = geo_result["display_name"]

            # Step 2: Build search criteria with coordinates
            current_criteria = SearchCriteria(
                query=query,  # Only for features, not location
                property_type=PropertyType(property_type) if property_type else None,
                listing_type=ListingType(listing_type) if listing_type else None,
                source=source,
                min_price=min_price,
                max_price=max_price,
                min_bedrooms=min_bedrooms,
                max_bedrooms=max_bedrooms,
                min_floors=min_floors,
                max_floors=max_floors,
                latitude=lat,
                longitude=lng,
                radius_km=radius_km,
                page=page,
                limit=10,
            )

            # Step 3: Use Hybrid Search if available
            if hybrid_service:
                result = run_async(hybrid_service.search(
                    adapter=adapter,
                    query=query or location_keyword,
                    property_type=property_type,
                    listing_type=listing_type,
                    source=source,
                    min_price=min_price,
                    max_price=max_price,
                    min_bedrooms=min_bedrooms,
                    max_bedrooms=max_bedrooms,
                    min_floors=min_floors,
                    max_floors=max_floors,
                    amenities=amenities,
                    in_complex=in_complex,
                    facing=facing,
                    latitude=lat,
                    longitude=lng,
                    radius_km=radius_km,
                    page=page,
                    limit=10,
                    use_semantic_rerank=True,
                    skip_chromadb_fallback=True,  # Don't fallback to ChromaDB when API empty
                ))

                properties = result.properties
                total = result.total
                has_more = result.has_more
                is_hybrid = result.reranked
                semantic_scores = result.semantic_scores
            else:
                # Fallback to API-only search
                api_result = run_async(adapter.search(current_criteria))
                properties = api_result.properties
                total = api_result.total
                has_more = api_result.has_more
                is_hybrid = False
                semantic_scores = {}

            # Store search state for pagination
            set_user_search_state(
                criteria=current_criteria,
                page=page,
                total=total,
                has_more=has_more,
            )

            if not properties:
                clear_user_search_results()
                clear_user_search_state()
                if page > 1:
                    return f"No more properties on page {page}."
                return f"No properties found within {radius_km}km of {location_keyword} ({display_name}). Try expanding radius or changing filters."

            # Cache results for reference by number
            results_cache = {}
            for i, prop in enumerate(properties[:10], 1):
                results_cache[i] = prop
            set_user_search_results(results_cache)

            # Format results
            search_type = "🔀 Hybrid" if is_hybrid else "📡 API"
            start_idx = (page - 1) * 10 + 1
            end_idx = min(page * 10, total)
            page_info = f"(Page {page}, showing {start_idx}-{end_idx} of {total})" if total > 10 else ""

            output_lines = [
                f"Found {total} properties within {radius_km}km of {location_keyword} ({search_type}) {page_info}:",
                f"📍 Center: {display_name}",
                f"📌 Coordinates: {lat:.6f}, {lng:.6f}",
            ]

            for i, prop in enumerate(properties[:10], 1):
                price_str = f"Rp {prop.price:,.0f}".replace(",", ".")
                features = []
                if prop.bedrooms:
                    features.append(f"{prop.bedrooms} BR")
                if prop.bathrooms:
                    features.append(f"{prop.bathrooms} BA")
                if prop.land_area:
                    features.append(f"LT {prop.land_area}m²")
                if prop.building_area:
                    features.append(f"LB {prop.building_area}m²")

                features_str = ", ".join(features) if features else ""

                # Source type indicator
                source_label = "🏗️ New" if prop.source_type == "project" else "🔄 Resale"
                developer_info = f" by {prop.developer_name}" if prop.developer_name else ""

                # Distance info
                distance_str = ""
                if prop.distance_km is not None:
                    if prop.distance_km < 1:
                        distance_str = f"📏 {prop.distance_km * 1000:.0f}m"
                    else:
                        distance_str = f"📏 {prop.distance_km:.1f}km"

                # URL
                url_line = f"\n   🔗 {prop.url_view}" if prop.url_view else ""

                output_lines.append(
                    f"\n{i}. **{prop.title}** {distance_str}\n"
                    f"   {source_label}{developer_info}{url_line}\n"
                    f"   📍 {prop.address or ''}, {prop.location or ''}\n"
                    f"   💰 {price_str} ({prop.listing_type})\n"
                    f"   🏠 {features_str}"
                )

            if has_more:
                output_lines.append(f"\n... and {total - end_idx} more properties. Use page={page + 1} for more.")

            # Record metrics
            tool_metrics.result_count = len(properties)
            tool_metrics.total_results = total

          except Exception as e:
            tool_metrics.error = str(e)
            return f"Error searching properties by location: {str(e)}"

        tool_metrics.duration_ms = timer.elapsed_ms
        get_metrics_collector().log_tool(tool_metrics)

        return "\n".join(output_lines)

    return [search_properties, search_properties_by_location, get_property_detail, get_property_by_number, geocode_location, search_nearby, search_pois]


def create_knowledge_tools(
    knowledge_vector_store: Optional[Chroma] = None,
    embeddings: Optional[OpenAIEmbeddings] = None,
) -> list:
    """
    Factory function to create knowledge/coaching-related tools.
    
    Args:
        knowledge_vector_store: Chroma vector store with knowledge base
        embeddings: Embeddings model for search
        
    Returns:
        List of LangChain tools
    """
    
    @tool(args_schema=SearchKnowledgeInput)
    def search_knowledge(
        query: str,
        category: Optional[str] = None,
    ) -> str:
        """
        Search the knowledge base for real estate information, sales techniques, or motivation.
        
        Use this when user asks:
        - Sales techniques: "how to close a deal?", "tips follow up"
        - Property knowledge: "what is SHM?", "bedanya SHM dan SHGB?"
        - Motivation: "butuh motivasi", "give me motivation"
        """
        try:
            if not knowledge_vector_store:
                # Fallback: return general info
                return (
                    "Knowledge base is not configured. "
                    "However, I can provide general real estate advice based on my training. "
                    f"Your question: {query}"
                )
            
            # Build filter if category provided
            filter_dict = None
            if category:
                filter_dict = {"category": category}
            
            # Search vector store
            docs = knowledge_vector_store.similarity_search(
                query=query,
                k=5,
                filter=filter_dict,
            )
            
            if not docs:
                return f"Tidak ditemukan informasi tentang '{query}' di knowledge base."
            
            # Format results
            output_lines = [f"Berikut informasi terkait '{query}':\n"]
            
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get("source", "Unknown")
                output_lines.append(f"**{i}. From: {source}**\n{doc.page_content}\n")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"Error searching knowledge base: {str(e)}"
    
    @tool
    def get_sales_tips(topic: str) -> str:
        """
        Get sales tips for real estate agents on a specific topic.
        
        Use for questions like:
        - "How to handle objections?"
        - "Tips for first meeting with client"
        - "Cara closing yang efektif"
        """
        # This could query vector store or return curated tips
        common_tips = {
            "closing": """
Tips untuk Closing yang Efektif:
1. Bangun trust terlebih dahulu - jangan buru-buru closing
2. Pahami kebutuhan dan concern klien
3. Gunakan teknik "assumptive close" - bicara seakan deal sudah terjadi
4. Atasi objection dengan empati, bukan argumen
5. Berikan deadline yang wajar untuk keputusan
6. Follow up secara konsisten tapi tidak mengganggu
""",
            "objection": """
Cara Handle Objection:
1. Dengarkan sampai selesai, jangan interrupt
2. Validasi concern mereka: "Saya mengerti..."
3. Tanyakan lebih detail: "Bisa jelaskan lebih lanjut?"
4. Berikan solusi, bukan excuses
5. Gunakan social proof jika ada
""",
            "follow_up": """
Tips Follow Up:
1. Follow up dalam 24 jam setelah meeting
2. Variasikan channel: WA, call, email
3. Berikan nilai tambah setiap follow up
4. Jangan hanya tanya "sudah ada keputusan?"
5. Update info property baru yang relevan
""",
        }
        
        # Find matching tips
        topic_lower = topic.lower()
        for key, tips in common_tips.items():
            if key in topic_lower or topic_lower in key:
                return tips
        
        return f"Berikut tips umum untuk {topic}:\n1. Pahami kebutuhan klien\n2. Bangun relationship\n3. Berikan value\n4. Follow up konsisten"
    
    @tool
    def get_motivation() -> str:
        """
        Get motivational message for real estate agent.
        
        Use when agent is feeling down or needs encouragement.
        """
        import random
        
        motivations = [
            """
🌟 Ingat, setiap "tidak" adalah langkah menuju "ya" berikutnya!

"Success is not final, failure is not fatal: it is the courage to continue that counts."
- Winston Churchill

Kamu sudah berani memilih karir sebagai agen properti. Itu sudah setengah dari kesuksesan.
Tetap semangat, hasil akan mengikuti usaha! 💪
""",
            """
💪 Hari ini mungkin berat, tapi ingat:

Setiap agen top pernah di posisimu sekarang. Yang membedakan adalah mereka tidak berhenti.

Tips untuk hari ini:
1. Fokus pada 1 prospek terbaik
2. Berikan service terbaik
3. Sisanya serahkan pada proses

Kamu bisa! 🚀
""",
            """
🔥 The harder you work, the luckier you get!

Di properti, konsistensi mengalahkan bakat.
Yang follow up 10x akan menang dari yang pintar tapi malas.

Terus bergerak, terus connect dengan orang.
Rezekimu tidak akan tertukar! 💫
""",
        ]
        
        return random.choice(motivations)
    
    return [search_knowledge, get_sales_tips, get_motivation]


def create_all_tools(
    property_adapter: PropertyDataAdapter,
    property_vector_store: Optional[Chroma] = None,
    knowledge_vector_store: Optional[Chroma] = None,
    embeddings: Optional[OpenAIEmbeddings] = None,
    property_store: Optional[PropertyStore] = None,
    use_hybrid_search: bool = True,
) -> list:
    """
    Create all tools for the agent.
    
    Args:
        property_adapter: Adapter for property API
        property_vector_store: Legacy vector store (deprecated, use property_store)
        knowledge_vector_store: Vector store for knowledge base
        embeddings: Embeddings model
        property_store: PropertyStore for hybrid search (ChromaDB)
        use_hybrid_search: Enable hybrid search (API + semantic re-ranking)
    
    Returns combined list of property and knowledge tools.
    """
    # Auto-initialize property_store if not provided and hybrid search is enabled
    if use_hybrid_search and property_store is None:
        try:
            from ..knowledge.property_store import create_property_store
            property_store = create_property_store()  # Uses absolute path
            logger.info("property_store_initialized", hybrid_search=True)
        except Exception as e:
            logger.warning("property_store_init_failed", error=str(e))
            property_store = None
    
    property_tools = create_property_tools(
        adapter=property_adapter,
        vector_store=property_vector_store,
        property_store=property_store,
        use_hybrid_search=use_hybrid_search,
    )
    
    knowledge_tools = create_knowledge_tools(
        knowledge_vector_store=knowledge_vector_store,
        embeddings=embeddings,
    )
    
    return property_tools + knowledge_tools
