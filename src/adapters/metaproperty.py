"""
MetaProperty API Adapter

Adapter for connecting to MetaProperty Laravel API.
Implements the PropertyDataAdapter interface for MetaProperty data source.
"""

import httpx
from typing import Optional
from datetime import datetime

from .base import (
    PropertyDataAdapter,
    Property,
    PropertyCreate,
    PropertyUpdate,
    SearchCriteria,
    SearchResult,
    PropertyType,
    ListingType,
    PropertyStatus,
    PropertyImage,
    PropertyAgent,
)
from ..utils.logging import get_api_logger

# Module logger
logger = get_api_logger()


# Mapping from MetaProperty property_type to our standard
METAPROPERTY_TYPE_MAP = {
    "house": PropertyType.HOUSE,
    "shophouse": PropertyType.SHOPHOUSE,
    "land": PropertyType.LAND,
    "apartment": PropertyType.APARTMENT,
    "warehouse": PropertyType.WAREHOUSE,
    "office": PropertyType.OFFICE,
    "villa": PropertyType.VILLA,
    # Indonesian aliases
    "rumah": PropertyType.HOUSE,
    "ruko": PropertyType.SHOPHOUSE,
    "tanah": PropertyType.LAND,
}

METAPROPERTY_STATUS_MAP = {
    "active": PropertyStatus.ACTIVE,
    "sold": PropertyStatus.SOLD,
    "sold_by_owner": PropertyStatus.SOLD,
    "rented": PropertyStatus.RENTED,
    "rented_by_owner": PropertyStatus.RENTED,
    "inactive": PropertyStatus.INACTIVE,
    "draft": PropertyStatus.INACTIVE,
}


class MetaPropertyAPIAdapter(PropertyDataAdapter):
    """
    Adapter for MetaProperty Laravel API.
    
    This adapter connects to the MetaProperty backend API to fetch
    and manage property listings.
    
    Configuration:
        - METAPROPERTY_API_URL: Base URL of the API (e.g., http://localhost:8000)
        - METAPROPERTY_API_TOKEN: Bearer token for authenticated requests
    """
    
    def __init__(
        self,
        api_url: str,
        api_token: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the MetaProperty adapter.
        
        Args:
            api_url: Base URL of MetaProperty API
            api_token: Bearer token for write operations
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.api_token = api_token
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def source_name(self) -> str:
        return "metaproperty"
    
    def _create_client(self) -> httpx.AsyncClient:
        """Create a new HTTP client (for use in context manager)"""
        headers = {"Accept": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        return httpx.AsyncClient(
            base_url=self.api_url,
            headers=headers,
            timeout=self.timeout,
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client - legacy method, prefer _create_client with context manager"""
        if self._client is None:
            headers = {"Accept": "application/json"}
            if self.api_token:
                headers["Authorization"] = f"Bearer {self.api_token}"

            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                headers=headers,
                timeout=self.timeout,
            )
        return self._client

    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # ==================== READ Operations ====================
    
    async def search(self, criteria: SearchCriteria) -> SearchResult:
        """
        Search properties via MetaProperty Unified API.

        Maps to: GET /api/v1/properties (unified endpoint for listings + projects)
        For geo search: GET /api/v1/properties?lat=...&lng=...&radius=...
        """
        # Use context manager to ensure client is properly closed
        # This avoids "Event loop is closed" errors when running multiple searches
        async with self._create_client() as client:
            # Build query parameters
            params = {
                "page": criteria.page,
                "per_page": criteria.limit,
            }

            # Source filter (listing/project/both)
            if criteria.source:
                params["source"] = criteria.source

            # Geospatial search parameters
            if criteria.latitude and criteria.longitude:
                params["lat"] = criteria.latitude
                params["lng"] = criteria.longitude
                if criteria.radius_km:
                    params["radius"] = criteria.radius_km

            # Map criteria to MetaProperty API parameters
            if criteria.query:
                params["search"] = criteria.query

            if criteria.property_type:
                params["property_type"] = criteria.property_type.value

            if criteria.listing_type:
                params["listing_type"] = criteria.listing_type.value

            if criteria.city:
                params["city"] = criteria.city

            if criteria.min_price:
                params["price_min"] = int(criteria.min_price)

            if criteria.max_price:
                params["price_max"] = int(criteria.max_price)

            # Bedroom filter (FIX: was accepted but not passed to API)
            if criteria.min_bedrooms:
                params["bedrooms_min"] = criteria.min_bedrooms

            if criteria.max_bedrooms:
                params["bedrooms_max"] = criteria.max_bedrooms

            # Floor filter (NEW)
            if criteria.min_floors:
                params["floors_min"] = criteria.min_floors

            if criteria.max_floors:
                params["floors_max"] = criteria.max_floors

            # Complex/Standalone filter
            if criteria.in_complex is not None:
                params["in_complex"] = "1" if criteria.in_complex else "0"

            # Facing direction filter
            if criteria.facing:
                params["facing"] = criteria.facing

            # Make API request to unified endpoint
            try:
                response = await client.get("/api/v1/properties", params=params)
                response.raise_for_status()
                data = response.json()

                # Parse response (unified format)
                properties = []
                for item in data.get("data", []):
                    prop = self._parse_unified_property(item)
                    if prop:
                        properties.append(prop)

                meta = data.get("meta", {})

                return SearchResult(
                    properties=properties,
                    total=meta.get("total", len(properties)),
                    page=meta.get("current_page", criteria.page),
                    limit=meta.get("per_page", criteria.limit),
                    has_more=meta.get("has_more", False),
                )

            except httpx.ConnectError as e:
                # Connection failed - server not running
                logger.error(
                    "api_connection_failed",
                    api_url=self.api_url,
                    error=str(e),
                    hint="Make sure the Laravel API server is running",
                )
                return SearchResult(
                    properties=[],
                    total=0,
                    page=criteria.page,
                    limit=criteria.limit,
                    has_more=False,
                )
            except httpx.HTTPStatusError as e:
                # HTTP error response (4xx, 5xx)
                logger.error(
                    "api_http_error",
                    status_code=e.response.status_code,
                    response_body=e.response.text[:200],
                )
                return SearchResult(
                    properties=[],
                    total=0,
                    page=criteria.page,
                    limit=criteria.limit,
                    has_more=False,
                )
            except httpx.HTTPError as e:
                # Other HTTP errors
                logger.error(
                    "api_error",
                    error_type=type(e).__name__,
                    error=str(e),
                )
                return SearchResult(
                    properties=[],
                    total=0,
                    page=criteria.page,
                    limit=criteria.limit,
                    has_more=False,
                )
    
    async def get_by_id(self, property_id: str) -> Optional[Property]:
        """
        Get a single property by ID or slug.
        
        Maps to: GET /api/v1/listings/{slug}
        """
        client = await self._get_client()
        
        try:
            response = await client.get(f"/api/v1/listings/{property_id}")
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and data.get("data"):
                return self._parse_listing(data["data"])
            return None
            
        except httpx.HTTPError:
            return None
    
    # ==================== WRITE Operations ====================
    
    async def create(
        self, 
        data: PropertyCreate, 
        agent_id: Optional[str] = None
    ) -> Property:
        """
        Create a new property listing.
        
        Maps to: POST /api/admin/listings
        Requires authentication.
        """
        if not self.api_token:
            raise PermissionError("API token required for write operations")
        
        client = await self._get_client()
        
        # Build request payload
        payload = {
            "title": data.title,
            "property_type": data.property_type.value,
            "listing_type": data.listing_type.value,
            "price": data.price,
            "district": data.location,
            "city": data.city,
        }
        
        if data.address:
            payload["display_address"] = data.address
        if data.bedrooms:
            payload["bedrooms"] = data.bedrooms
        if data.bathrooms:
            payload["bathrooms"] = data.bathrooms
        if data.land_area:
            payload["land_area"] = data.land_area
        if data.building_area:
            payload["building_area"] = data.building_area
        if data.floors:
            payload["floors"] = data.floors
        if data.description:
            payload["description"] = data.description
        if data.certificate_type:
            payload["certificate_type"] = data.certificate_type
        
        try:
            response = await client.post("/api/admin/listings", json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("data"):
                return self._parse_listing(result["data"])
            raise ValueError("Failed to create listing")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise PermissionError("Not authorized to create listings")
            raise ValueError(f"API error: {e.response.text}")
    
    async def update(
        self, 
        property_id: str, 
        data: PropertyUpdate,
        agent_id: Optional[str] = None
    ) -> Property:
        """
        Update an existing property.
        
        Maps to: PUT /api/admin/listings/{id}
        Requires authentication and ownership.
        """
        if not self.api_token:
            raise PermissionError("API token required for write operations")
        
        client = await self._get_client()
        
        # Build update payload (only include non-None fields)
        payload = {}
        if data.title is not None:
            payload["title"] = data.title
        if data.price is not None:
            payload["price"] = data.price
        if data.status is not None:
            payload["status"] = data.status.value
        if data.description is not None:
            payload["description"] = data.description
        if data.bedrooms is not None:
            payload["bedrooms"] = data.bedrooms
        if data.bathrooms is not None:
            payload["bathrooms"] = data.bathrooms
        if data.land_area is not None:
            payload["land_area"] = data.land_area
        if data.building_area is not None:
            payload["building_area"] = data.building_area
        
        try:
            response = await client.put(
                f"/api/admin/listings/{property_id}", 
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("data"):
                return self._parse_listing(result["data"])
            raise ValueError("Failed to update listing")
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise PermissionError("Not authorized to update this listing")
            if e.response.status_code == 404:
                raise ValueError(f"Property {property_id} not found")
            raise ValueError(f"API error: {e.response.text}")
    
    async def delete(
        self, 
        property_id: str,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Delete (deactivate) a property listing.
        
        Maps to: DELETE /api/admin/listings/{id}
        """
        if not self.api_token:
            raise PermissionError("API token required for write operations")
        
        client = await self._get_client()
        
        try:
            response = await client.delete(f"/api/admin/listings/{property_id}")
            response.raise_for_status()
            return True
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                raise PermissionError("Not authorized to delete this listing")
            if e.response.status_code == 404:
                raise ValueError(f"Property {property_id} not found")
            return False
    
    # ==================== Helper Methods ====================

    def _parse_unified_property(self, data: dict) -> Optional[Property]:
        """Parse unified API response (from /api/v1/properties) into Property model"""
        try:
            # Parse property type
            raw_type = data.get("property_type", "house")
            property_type = METAPROPERTY_TYPE_MAP.get(raw_type, PropertyType.HOUSE)

            # Parse listing type
            raw_listing = data.get("listing_type", "sale")
            listing_type = ListingType.SALE if raw_listing == "sale" else ListingType.RENT

            # Parse source type (listing = secondary, project = primary)
            source_type = data.get("source", "listing")

            # Parse status
            raw_status = data.get("status", "active")
            status = METAPROPERTY_STATUS_MAP.get(raw_status, PropertyStatus.ACTIVE)

            # Parse handler/agent info
            agent = None
            developer_name = None

            # Check for agent data (from listings)
            agent_data = data.get("agent") or data.get("handler")
            if agent_data:
                if agent_data.get("type") == "developer":
                    developer_name = agent_data.get("name")
                agent = PropertyAgent(
                    id=str(agent_data.get("id", "")),
                    name=agent_data.get("name", ""),
                    phone=agent_data.get("phone"),
                    whatsapp=agent_data.get("whatsapp"),
                    photo_url=agent_data.get("photo"),
                    office=agent_data.get("office") or agent_data.get("branch_name"),
                )

            # Parse images
            images = []
            for img_data in data.get("images", []):
                images.append(PropertyImage(
                    url=img_data.get("image_url", ""),
                    thumb_url=img_data.get("thumb_url"),
                    is_cover=img_data.get("is_cover", False),
                ))

            # Fallback to cover_image field
            if not images and data.get("cover_image"):
                images.append(PropertyImage(
                    url=data["cover_image"],
                    thumb_url=data.get("cover_image_thumb") or data["cover_image"],
                    is_cover=True,
                ))

            return Property(
                id=str(data.get("uuid") or data.get("id", "")),
                source=self.source_name,
                source_type=source_type,
                url_view=data.get("url_view"),
                title=data.get("title") or data.get("name", ""),
                property_type=property_type,
                listing_type=listing_type,
                price=float(data.get("price", 0)),
                location=data.get("location") or data.get("district") or data.get("display_address") or "",
                city=data.get("city", ""),
                address=data.get("display_address") or data.get("address"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                bedrooms=data.get("bedrooms"),
                bathrooms=data.get("bathrooms"),
                land_area=data.get("land_area"),
                building_area=data.get("building_area"),
                floors=data.get("floors"),
                description=data.get("description"),
                features=data.get("amenities") or data.get("facilities") or [],
                certificate_type=data.get("certificate_type"),
                images=images,
                agent=agent,
                developer_name=developer_name,
                status=status,
                created_at=self._parse_datetime(data.get("created_at")),
                updated_at=self._parse_datetime(data.get("updated_at")),
                distance_km=data.get("distance"),  # Distance from geo search
            )

        except Exception as e:
            logger.warning("parse_unified_property_failed", error=str(e), data_id=data.get("id"))
            return None

    def _parse_listing(self, data: dict) -> Optional[Property]:
        """Parse MetaProperty API response into Property model"""
        try:
            # Parse property type
            raw_type = data.get("property_type", "house")
            property_type = METAPROPERTY_TYPE_MAP.get(raw_type, PropertyType.HOUSE)
            
            # Parse listing type
            raw_listing = data.get("listing_type", "sale")
            listing_type = ListingType.SALE if raw_listing == "sale" else ListingType.RENT
            
            # Parse status
            raw_status = data.get("status", "active")
            status = METAPROPERTY_STATUS_MAP.get(raw_status, PropertyStatus.ACTIVE)
            
            # Parse images
            images = []
            for img_data in data.get("images", []):
                images.append(PropertyImage(
                    url=img_data.get("image_url", ""),
                    thumb_url=img_data.get("thumb_url"),
                    is_cover=img_data.get("is_cover", False),
                ))
            
            # Also check for cover_image field
            if not images and data.get("cover_image"):
                images.append(PropertyImage(
                    url=data["cover_image"],
                    thumb_url=data.get("cover_image_thumb"),
                    is_cover=True,
                ))
            
            # Parse agent
            agent = None
            agent_data = data.get("agent") or data.get("handler")
            if agent_data:
                agent = PropertyAgent(
                    id=str(agent_data.get("id", "")),
                    name=agent_data.get("name", ""),
                    phone=agent_data.get("phone"),
                    whatsapp=agent_data.get("whatsapp"),
                    photo_url=agent_data.get("photo"),
                    office=agent_data.get("office") or agent_data.get("branch_name"),
                )
            
            # Build Property object
            return Property(
                id=str(data.get("uuid") or data.get("id")),
                source=self.source_name,
                title=data.get("title", ""),
                property_type=property_type,
                listing_type=listing_type,
                price=float(data.get("price", 0)),
                location=data.get("district") or data.get("display_address") or "",
                city=data.get("city", ""),
                address=data.get("display_address") or data.get("address"),
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                bedrooms=data.get("bedrooms"),
                bathrooms=data.get("bathrooms"),
                land_area=data.get("land_area"),
                building_area=data.get("building_area"),
                floors=data.get("floors"),
                description=data.get("description"),
                features=data.get("amenities") or [],
                certificate_type=data.get("certificate_type"),
                images=images,
                agent=agent,
                status=status,
                created_at=self._parse_datetime(data.get("created_at")),
                updated_at=self._parse_datetime(data.get("updated_at")),
            )
            
        except Exception as e:
            logger.warning("parse_listing_failed", error=str(e), data_id=data.get("id"))
            return None
    
    def _parse_datetime(self, value: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API"""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    # ==================== Sync Operations (for ChromaDB) ====================
    
    async def get_pending_ingest(self, limit: int = 100) -> list[dict]:
        """
        Get listings that need to be ingested to ChromaDB.
        
        Requires MetaProperty API endpoint: GET /api/v1/sync/pending-ingest
        
        Args:
            limit: Max number of listings to fetch
            
        Returns:
            List of listing dicts with id, title, description, etc.
        """
        client = await self._get_client()
        response = await client.get(
            "/api/v1/sync/pending-ingest",
            params={"limit": limit}
        )
        response.raise_for_status()
        return response.json().get("data", [])
    
    async def mark_ingested(self, items: list[dict]) -> bool:
        """
        Mark properties as successfully ingested to ChromaDB.
        
        Requires MetaProperty API endpoint: POST /api/v1/sync/mark-ingested
        
        Args:
            items: List of dicts with 'source' and 'id' keys
                   e.g., [{"source": "listing", "id": 1}, {"source": "project", "id": 2}]
            
        Returns:
            True if successful
        """
        client = await self._get_client()
        
        # Build the ids array in expected format
        ids = [{"source": item["source"], "id": item["id"]} for item in items]
        
        response = await client.post(
            "/api/v1/sync/mark-ingested",
            json={"ids": ids}
        )
        response.raise_for_status()
        return response.json().get("success", False)
    
    async def reset_ingest_flags(self) -> bool:
        """
        Reset all need_ingest flags to true (for full re-sync).
        
        Requires MetaProperty API endpoint: POST /api/v1/sync/reset-ingest
        
        Returns:
            True if successful
        """
        client = await self._get_client()
        response = await client.post("/api/v1/sync/reset-ingest")
        response.raise_for_status()
        return response.json().get("success", False)
    
    async def get_sync_stats(self) -> dict:
        """
        Get sync statistics from MetaProperty API.
        
        Requires MetaProperty API endpoint: GET /api/v1/sync/stats
        
        Returns:
            Dict with total_listings, pending_ingest, already_synced, sync_percentage
        """
        client = await self._get_client()
        response = await client.get("/api/v1/sync/stats")
        response.raise_for_status()
        return response.json().get("data", {})

