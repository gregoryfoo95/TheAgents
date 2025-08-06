# settings.py
import json
import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1) Load all keys from .env into os.environ
load_dotenv(".env")


class Settings(BaseSettings):
    """All application settings pulled from environment variables."""

    # Tell Pydantic where to find .env and that variable names are case-insensitive
    model_config = SettingsConfigDict(
        env_file=None,        # we've already loaded .env ourselves
        case_sensitive=False,
    )

    # Database
    database_url: str = Field(
        default="postgresql://postgres:postgres123@localhost:5432/property_marketplace"
    )
    async_database_url: str = Field(default="")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379")

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # API
    api_title: str = Field(default="Property Marketplace API")
    api_description: str = Field(
        default="A comprehensive property marketplace with AI-powered features"
    )
    api_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)

    # CORS
    allowed_origins: list[str] = Field(default_factory=list)

    # File upload
    max_file_size: int = Field(default=10 * 1024 * 1024)
    allowed_image_types: set[str] = Field(default_factory=set)
    allowed_document_types: set[str] = Field(default_factory=set)

    # AI services
    openai_api_key: str = Field(default="")

    # Pagination
    default_page_size: int = Field(default=20)
    max_page_size: int = Field(default=100)

    # OAuth 2.0
    google_client_id: str = Field(default="")
    google_client_secret: str = Field(default="")
    oauth_redirect_uri: str = Field(
        default="http://localhost:8000/api/auth/callback/google"
    )

    # JWT
    jwt_secret_key: str = Field(default="fallback-jwt-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_access_token_expire_minutes: int = Field(default=15)
    jwt_refresh_token_expire_days: int = Field(default=30)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # derive async URL if not set
        if not self.async_database_url:
            self.async_database_url = self.database_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            )
    #
    # Validators to parse JSON‐style env strings into Python collections
    #

    @field_validator("allowed_origins", mode="before")
    def _parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

    @field_validator("allowed_image_types", mode="before")
    def _parse_allowed_image_types(cls, v):
        if isinstance(v, str):
            return set(json.loads(v))
        return v

    @field_validator("allowed_document_types", mode="before")
    def _parse_allowed_document_types(cls, v):
        if isinstance(v, str):
            return set(json.loads(v))
        return v

@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (populated from os.environ)."""
    return Settings()
