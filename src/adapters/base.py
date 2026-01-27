"""
Base Data Adapter Interface and Data Models

This module defines the universal interface that all property data sources
must implement. This allows the RAG system to work with any data source
(MetaProperty, Rumah123, OLX, etc.) through a consistent API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Optional, Any
from enum import Enum


class PropertyType(str, Enum):
    """Standardized property types across all sources"""
    HOUSE = "house"           # rumah
    SHOPHOUSE = "shophouse"   # ruko
    LAND = "land"             # tanah
    APARTMENT = "apartment"   # apartment
    WAREHOUSE = "warehouse"   # gudang
    OFFICE = "office"         # kantor
    VILLA = "villa"           # villa


class ListingType(str, Enum):
    """Listing type: for sale or rent"""
    SALE = "sale"
    RENT = "rent"


class PropertyStatus(str, Enum):
    """Property availability status"""
    ACTIVE = "active"
    SOLD = "sold"
    RENTED = "rented"
    INACTIVE = "inactive"


@dataclass
class PropertyImage:
    """Standard property image format"""
    url: str
    thumb_url: Optional[str] = None
    is_cover: bool = False
    caption: Optional[str] = None


@dataclass
class PropertyAgent:
    """Agent/owner information for a property"""
    id: Optional[str] = None
    name: str = ""
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    photo_url: Optional[str] = None
    office: Optional[str] = None


@dataclass
class Property:
    """
    Standard property data model.
    All adapters must transform their source data to this format.
    """
    # Required fields
    id: str
    source: str                  # e.g., "metaproperty", "rumah123"
    title: str
    property_type: PropertyType
    listing_type: ListingType
    price: float

    # Location
    location: str               # Area/district name
    city: str

    # Source type (primary/secondary market)
    source_type: str = "listing"  # "listing" (secondary) or "project" (primary)
    developer_name: Optional[str] = None  # For projects
    url_view: Optional[str] = None  # Full URL to property detail page

    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Specifications
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    land_area: Optional[float] = None       # in sqm
    building_area: Optional[float] = None   # in sqm
    floors: Optional[int] = None
    
    # Additional info
    description: Optional[str] = None
    features: list[str] = field(default_factory=list)
    certificate_type: Optional[str] = None  # SHM, SHGB, etc.
    
    # Media
    images: list[PropertyImage] = field(default_factory=list)
    
    # Agent/handler
    agent: Optional[PropertyAgent] = None
    
    # Status
    status: PropertyStatus = PropertyStatus.ACTIVE
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Search relevance (populated after search)
    relevance_score: Optional[float] = None
    match_reason: Optional[str] = None

    # Distance (populated after geo search)
    distance_km: Optional[float] = None  # Distance in kilometers from search point
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "source": self.source,
            "source_type": self.source_type,
            "url_view": self.url_view,
            "title": self.title,
            "property_type": self.property_type.value,
            "listing_type": self.listing_type.value,
            "price": self.price,
            "location": self.location,
            "city": self.city,
            "address": self.address,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "land_area": self.land_area,
            "building_area": self.building_area,
            "floors": self.floors,
            "description": self.description,
            "features": self.features,
            "certificate_type": self.certificate_type,
            "images": [{"url": img.url, "thumb_url": img.thumb_url} for img in self.images],
            "agent": {
                "name": self.agent.name,
                "phone": self.agent.phone,
            } if self.agent else None,
            "developer_name": self.developer_name,
            "status": self.status.value,
        }
    
    def to_embedding_text(self) -> str:
        """Generate text for vector embedding"""
        parts = [
            self.title,
            f"Tipe: {self.property_type.value}",
            f"Lokasi: {self.location}, {self.city}",
            f"Harga: Rp {self.price:,.0f}",
        ]
        
        if self.bedrooms:
            parts.append(f"{self.bedrooms} kamar tidur")
        if self.bathrooms:
            parts.append(f"{self.bathrooms} kamar mandi")
        if self.land_area:
            parts.append(f"Luas tanah {self.land_area}m²")
        if self.building_area:
            parts.append(f"Luas bangunan {self.building_area}m²")
        if self.features:
            parts.append(f"Fitur: {', '.join(self.features)}")
        if self.description:
            parts.append(self.description)
            
        return ". ".join(parts)


@dataclass
class SearchCriteria:
    """Search criteria for property lookup"""
    query: Optional[str] = None              # Free text search
    property_type: Optional[PropertyType] = None
    listing_type: Optional[ListingType] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    location: Optional[str] = None
    city: Optional[str] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[int] = None
    min_land_area: Optional[float] = None
    min_building_area: Optional[float] = None
    min_floors: Optional[int] = None         # Minimum number of floors/stories
    max_floors: Optional[int] = None         # Maximum number of floors/stories
    features: list[str] = field(default_factory=list)
    amenities: list[str] = field(default_factory=list)  # Required amenities (cctv, wifi, etc.)

    # Source filter: "listing" (secondary), "project" (primary), or None (both)
    source: Optional[str] = None

    # Complex/Standalone filter
    in_complex: Optional[bool] = None        # True=in complex, False=standalone, None=both

    # Facing direction filter (utara, selatan, timur, barat, etc.)
    facing: Optional[str] = None

    # Location search (smart lookup)
    location_keyword: Optional[str] = None   # Location keyword for smart API lookup (checked in district/city first)

    # Geospatial search (fallback when location_keyword not found in DB)
    latitude: Optional[float] = None         # Center point latitude
    longitude: Optional[float] = None        # Center point longitude
    radius_km: Optional[float] = None        # Search radius in kilometers

    # Pagination
    page: int = 1
    limit: int = 10


@dataclass
class PropertyCreate:
    """Data required to create a new property listing"""
    title: str
    property_type: PropertyType
    listing_type: ListingType
    price: float
    location: str
    city: str
    address: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    land_area: Optional[float] = None
    building_area: Optional[float] = None
    floors: Optional[int] = None
    description: Optional[str] = None
    features: list[str] = field(default_factory=list)
    certificate_type: Optional[str] = None


@dataclass
class PropertyUpdate:
    """Data for updating an existing property"""
    title: Optional[str] = None
    price: Optional[float] = None
    status: Optional[PropertyStatus] = None
    description: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    land_area: Optional[float] = None
    building_area: Optional[float] = None
    features: Optional[list[str]] = None


@dataclass
class SearchResult:
    """Paginated search result"""
    properties: list[Property]
    total: int
    page: int
    limit: int
    has_more: bool


class PropertyDataAdapter(ABC):
    """
    Abstract base class for property data adapters.
    
    All data sources (MetaProperty, Rumah123, OLX, etc.) must implement
    this interface to be compatible with the RAG system.
    """
    
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source (e.g., 'metaproperty')"""
        pass
    
    # ==================== READ Operations ====================
    
    @abstractmethod
    async def search(self, criteria: SearchCriteria) -> SearchResult:
        """
        Search properties based on criteria.
        
        Args:
            criteria: Search parameters (type, price range, location, etc.)
            
        Returns:
            SearchResult with matching properties and pagination info
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, property_id: str) -> Optional[Property]:
        """
        Get a single property by its ID.
        
        Args:
            property_id: The property's unique identifier
            
        Returns:
            Property if found, None otherwise
        """
        pass
    
    async def get_all(self, page: int = 1, limit: int = 20) -> SearchResult:
        """
        Get all properties with pagination.
        Default implementation calls search with empty criteria.
        """
        return await self.search(SearchCriteria(page=page, limit=limit))
    
    # ==================== WRITE Operations ====================
    # These require authentication and permission checks
    
    @abstractmethod
    async def create(
        self, 
        data: PropertyCreate, 
        agent_id: Optional[str] = None
    ) -> Property:
        """
        Create a new property listing.
        
        Args:
            data: Property creation data
            agent_id: ID of the agent creating this listing
            
        Returns:
            The created Property
            
        Raises:
            PermissionError: If agent is not authorized
            ValueError: If data is invalid
        """
        pass
    
    @abstractmethod
    async def update(
        self, 
        property_id: str, 
        data: PropertyUpdate,
        agent_id: Optional[str] = None
    ) -> Property:
        """
        Update an existing property.
        
        Args:
            property_id: ID of property to update
            data: Fields to update
            agent_id: ID of agent making the update (for permission check)
            
        Returns:
            The updated Property
            
        Raises:
            PermissionError: If agent doesn't own this listing
            ValueError: If property not found
        """
        pass
    
    @abstractmethod
    async def delete(
        self, 
        property_id: str,
        agent_id: Optional[str] = None
    ) -> bool:
        """
        Delete (or deactivate) a property listing.
        
        Args:
            property_id: ID of property to delete
            agent_id: ID of agent making the deletion
            
        Returns:
            True if deleted successfully
            
        Raises:
            PermissionError: If agent doesn't own this listing
        """
        pass
    
    # ==================== Permission Check ====================
    
    async def check_ownership(
        self, 
        property_id: str, 
        agent_id: str
    ) -> bool:
        """
        Check if an agent owns a specific property.
        Default implementation fetches property and checks agent ID.
        """
        property = await self.get_by_id(property_id)
        if not property or not property.agent:
            return False
        return property.agent.id == agent_id
