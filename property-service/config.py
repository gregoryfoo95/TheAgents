from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "property-service"
    api_host: str = "0.0.0.0"
    api_port: int = 8002
    debug: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    property_database_url: str = os.getenv(
        "PROPERTY_DATABASE_URL",
        "postgresql://property_user:property_password@localhost:5432/property_db"
    )
    
    # Auth Service Configuration
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    
    # File Upload Configuration
    upload_dir: str = "/app/uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_image_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Redis Configuration
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    
    # CORS Configuration
    allowed_origins: Union[List[str], str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:8000"
    )
    
    @field_validator('allowed_origins')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()