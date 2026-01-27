"""
Request Schemas for API endpoints
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field
import uuid


class ChatRequest(BaseModel):
    """Chat request payload"""

    message: str = Field(
        ...,
        description="User message to the assistant",
        min_length=1,
        max_length=2000,
        examples=["Cari rumah di cemara asri medan"],
    )

    session_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Session ID for conversation continuity. Auto-generated if not provided.",
    )

    user_id: Optional[str] = Field(
        default="anonymous",
        description="User ID for isolation and tracking",
    )

    method: Literal["hybrid", "api_only", "vector_only"] = Field(
        default="hybrid",
        description="Search method to use. Hybrid recommended for best results.",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Cari rumah 3 kamar di medan harga di bawah 2M",
                "session_id": "user-123-session-456",
                "method": "hybrid",
            }
        }
