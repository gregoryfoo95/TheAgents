"""Configuration management for Stock AI Service"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_host: str
    api_port: int
    debug: bool
    
    # Database Configuration
    stock_database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    
    # OpenAI Configuration
    openai_api_key: str
    
    # LLM Configuration
    llm_model: str
    llm_temperature: float
    
    # External APIs
    yahoo_finance_api: str
    alpha_vantage_api_key: Optional[str] = None
    
    # Logging
    log_level: str
    
    # Rate Limiting
    analysis_rate_limit: int
    api_timeout: int
    
    # Cache Configuration
    redis_url: str
    cache_ttl: int
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get the database URL for the stock AI service"""
    return settings.stock_database_url


def get_openai_config() -> dict:
    """Get OpenAI configuration"""
    return {
        "api_key": settings.openai_api_key,
        "model": settings.llm_model,
        "temperature": settings.llm_temperature
    }


def get_redis_config() -> dict:
    """Get Redis configuration"""
    return {
        "url": settings.redis_url,
        "ttl": settings.cache_ttl
    }