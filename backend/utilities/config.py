from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/property_marketplace"
    async_database_url: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API
    api_title: str = "Property Marketplace API"
    api_description: str = "A comprehensive property marketplace with AI-powered features"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # CORS
    allowed_origins: list[str] = ["http://localhost:3000"]
    
    # File upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: set[str] = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    allowed_document_types: set[str] = {
        "application/pdf", 
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain"
    }
    
    # AI Services
    openai_api_key: str = ""
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.async_database_url:
            self.async_database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 