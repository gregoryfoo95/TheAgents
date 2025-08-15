from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List, Union

class Settings(BaseSettings):
    # Service Configuration
    service_name: str = "auth-service"
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    debug: bool = False
    log_level: str = "INFO"
    
    # Database Configuration
    auth_database_url: str = Field(
        default="postgresql://auth_user:auth_password@localhost:5431/auth_db",
        alias="AUTH_DATABASE_URL"
    )
    
    # JWT Configuration
    jwt_secret: str = Field(
        default="your-super-secret-jwt-key-here",
        alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # OAuth Configuration
    google_client_id: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, alias="GOOGLE_CLIENT_SECRET")
    oauth_redirect_uri: str = Field(
        default="http://localhost:8000/auth/callback/google",
        alias="OAUTH_REDIRECT_URI"
    )
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # CORS Configuration
    allowed_origins: Union[List[str], str] = Field(
        default="http://localhost:3000,http://localhost:8000",
        alias="ALLOWED_ORIGINS"
    )
    
    @field_validator('allowed_origins')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    model_config = {"env_file": ".env", "case_sensitive": False, "extra": "allow"}

settings = Settings()