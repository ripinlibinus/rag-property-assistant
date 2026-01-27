"""
Health Check Router
"""
from fastapi import APIRouter

from ..config import get_settings
from ..schemas import HealthResponse, MethodsResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns service status, version, and environment.
    """
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/methods", response_model=MethodsResponse)
async def get_methods():
    """
    Get available search methods.
    Returns list of methods with descriptions.
    """
    return MethodsResponse(
        methods=["hybrid", "api_only", "vector_only"],
        default="hybrid",
        descriptions={
            "hybrid": "Combines API filtering with semantic re-ranking. Best accuracy (100% in evaluation).",
            "api_only": "Uses only the property API with filters. Fast but may miss semantic matches.",
            "vector_only": "Uses only ChromaDB semantic search. Good for vague queries.",
        },
    )
