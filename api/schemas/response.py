"""
Response Schemas for API endpoints
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class PropertySummary(BaseModel):
    """Summary of a property in search results"""

    id: int = Field(..., description="Property ID")
    title: str = Field(..., description="Property title")
    price: int = Field(..., description="Price in IDR")
    price_formatted: str = Field(..., description="Formatted price (e.g., 'Rp 1,5 M')")
    location: str = Field(..., description="Property location/district")
    city: str = Field(..., description="City name")
    property_type: str = Field(..., description="Type: house, apartment, shophouse, etc.")
    listing_type: str = Field(..., description="sale or rent")
    source_type: Optional[str] = Field(None, description="project (primary) or listing (secondary)")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms")
    land_area: Optional[int] = Field(None, description="Land area in sqm")
    building_area: Optional[int] = Field(None, description="Building area in sqm")
    url: Optional[str] = Field(None, description="Property detail URL")


class SearchMetadata(BaseModel):
    """Metadata about the search operation"""

    total_found: int = Field(..., description="Total properties found")
    returned: int = Field(..., description="Number of properties returned")
    method_used: str = Field(..., description="Search method used")
    has_more: bool = Field(False, description="Whether more results are available")


class ChatResponse(BaseModel):
    """Chat response payload"""

    response: str = Field(..., description="Natural language response from the assistant")
    properties: List[PropertySummary] = Field(
        default_factory=list,
        description="List of matching properties (if any)",
    )
    session_id: str = Field(..., description="Session ID for conversation continuity")
    metadata: SearchMetadata = Field(..., description="Search metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Berikut 5 rumah di Medan dengan harga di bawah 2M:\n\n1. Rumah Minimalis Cemara Asri...",
                "properties": [
                    {
                        "id": 123,
                        "title": "Rumah Minimalis Cemara Asri",
                        "price": 1500000000,
                        "price_formatted": "Rp 1,5 M",
                        "location": "Cemara Asri",
                        "city": "Medan",
                        "property_type": "house",
                        "listing_type": "sale",
                        "bedrooms": 3,
                        "bathrooms": 2,
                    }
                ],
                "session_id": "user-123-session-456",
                "metadata": {
                    "total_found": 15,
                    "returned": 5,
                    "method_used": "hybrid",
                    "has_more": True,
                },
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (development/production)")


class MethodsResponse(BaseModel):
    """Available search methods response"""

    methods: List[str] = Field(
        ...,
        description="List of available search methods",
        examples=[["hybrid", "api_only", "vector_only"]],
    )
    default: str = Field("hybrid", description="Default recommended method")
    descriptions: dict = Field(
        ...,
        description="Description of each method",
    )
