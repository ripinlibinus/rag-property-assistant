"""
RAG Property Search API - FastAPI Application

Production-ready API for the RAG Property Search Assistant.

Usage:
    uvicorn api.main:app --reload --port 8000

Endpoints:
    GET  /api/v1/health     - Health check
    GET  /api/v1/methods    - Available search methods
    POST /api/v1/chat       - Main chat endpoint
    POST /api/v1/chat/stream - Streaming chat endpoint
    GET  /docs              - Swagger UI documentation
    GET  /redoc             - ReDoc documentation
"""
import os
import sys
import logging
from contextlib import asynccontextmanager
from pathlib import Path

# Load environment variables BEFORE any other imports
from dotenv import load_dotenv
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to path for imports
sys.path.insert(0, str(project_root))

from api.config import get_settings
from api.routers import chat_router, health_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Runs on startup and shutdown.
    """
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Pre-load the agent (optional, for faster first request)
    # from api.dependencies import get_agent
    # get_agent()
    # logger.info("Agent pre-loaded")

    yield

    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="""
RAG Property Search Assistant API

A production-ready API for searching properties using a hybrid RAG approach:
- **Hybrid Search**: Combines API filtering with semantic re-ranking (100% accuracy)
- **API-only Search**: Uses only the property API with filters
- **Vector-only Search**: Uses only ChromaDB semantic search

## Key Features
- Multi-turn conversation with session management
- Support for Indonesian and English queries
- Real-time streaming responses
- Multiple search methods for different use cases

## Evaluation Results
- Hybrid: 100% accuracy, F1=1.0
- API-only: 73.33% accuracy
- Vector-only: 56.67% accuracy
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


# Serve frontend static files (if built)
frontend_dist = os.path.join(project_root, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        """Serve the frontend SPA"""
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        """Serve frontend for all routes (SPA routing)"""
        file_path = os.path.join(frontend_dist, path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        """Root endpoint - API info"""
        return {
            "message": "RAG Property Search API",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
