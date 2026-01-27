"""
Application configuration using Pydantic Settings
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # LLM Configuration
    openai_api_key: str = Field(..., description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o-mini", description="LLM model to use")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", 
        description="Embedding model"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/rag_property",
        description="PostgreSQL connection string"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    redis_session_ttl: int = Field(default=3600, description="Session TTL in seconds")
    
    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./data/chroma",
        description="ChromaDB persistence directory"
    )
    chroma_collection_name: str = Field(
        default="properties",
        description="ChromaDB collection name"
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_debug: bool = Field(default=True, description="Debug mode")
    
    # WhatsApp Forwarder
    whatsapp_forwarder_url: str = Field(
        default="http://localhost:3001",
        description="WhatsApp forwarder URL"
    )
    whatsapp_webhook_secret: str = Field(
        default="",
        description="Webhook secret for verification"
    )
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Log level"
    )
    log_format: Literal["json", "console"] = Field(
        default="json",
        description="Log format"
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience alias
settings = get_settings()
