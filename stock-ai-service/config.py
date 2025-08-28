"""Configuration management for Stock AI Service"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8003
    debug: bool = True
    
    # Database Configuration
    stock_database_url: str = "postgresql://stock_user:password@postgres-stock:5432/stock_ai_db"
    postgres_user: str = "stock_user"
    postgres_password: str = "password"
    postgres_db: str = "stock_ai_db"
    postgres_host: str = "postgres-stock"
    postgres_port: int = 5432
    
    # OpenAI Configuration (fallback)
    openai_api_key: Optional[str] = None
    
    # AWS Bedrock Configuration
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    bedrock_model_id: str = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    # LLM Configuration
    llm_provider: str = "bedrock"  # "bedrock" or "openai"
    llm_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    llm_temperature: float = 0.7
    
    # External APIs
    yahoo_finance_api: str = "https://finance.yahoo.com"
    alpha_vantage_api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    
    # Rate Limiting
    analysis_rate_limit: int = 10
    api_timeout: int = 60
    
    # Cache Configuration
    redis_url: str = "redis://redis:6379/0"
    cache_ttl: int = 3600
    
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


def get_bedrock_config() -> dict:
    """Get AWS Bedrock configuration"""
    return {
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
        "model_id": settings.bedrock_model_id,
        "temperature": settings.llm_temperature
    }


def get_llm_config() -> dict:
    """Get LLM configuration based on provider"""
    if settings.llm_provider == "bedrock":
        return {
            "provider": "bedrock",
            **get_bedrock_config()
        }
    else:
        return {
            "provider": "openai", 
            **get_openai_config()
        }


def get_redis_config() -> dict:
    """Get Redis configuration"""
    return {
        "url": settings.redis_url,
        "ttl": settings.cache_ttl
    }