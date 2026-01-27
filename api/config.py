"""
API Configuration using Pydantic Settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App
    app_name: str = "RAG Property Search API"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    # MetaProperty API
    metaproperty_api_url: str = "http://localhost:8000"
    metaproperty_api_token: Optional[str] = None

    # ChromaDB
    chroma_persist_directory: str = "./data/chromadb"

    # Database (SQLite for chat history)
    database_path: str = "./data/chat_history.db"

    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
