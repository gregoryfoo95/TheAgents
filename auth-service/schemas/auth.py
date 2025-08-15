from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from models.user import UserType

# Request schemas - OAuth only
class OAuthCallbackRequest(BaseModel):
    """OAuth callback with authorization code"""
    code: str
    state: Optional[str] = None
    provider: str  # google, github, microsoft, linkedin

class TokenRefreshRequest(BaseModel):
    refresh_token: str

# Response schemas
class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    profile_picture_url: Optional[str]
    user_type: Optional[UserType]
    is_active: bool
    is_verified: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class MessageResponse(BaseModel):
    message: str

# Token validation schemas
class TokenPayload(BaseModel):
    sub: str  # User ID
    email: str
    user_type: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    exp: int
    iat: int
    type: str

class UserValidationResponse(BaseModel):
    user_id: int
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    user_type: Optional[UserType]
    is_active: bool
    is_verified: bool


# OAuth Schemas
class OAuthProvidersResponse(BaseModel):
    providers: List[str]


class AuthCallbackResponse(BaseModel):
    success: bool
    message: str
    tokens: LoginResponse
    user: Dict[str, Any]


class UserTypeSelectionData(BaseModel):
    user_type: str
    phone: Optional[str] = None
    
    @validator('user_type')
    def validate_user_type(cls, v):
        valid_types = ['consumer', 'agent', 'lawyer']
        if v not in valid_types:
            raise ValueError(f'user_type must be one of: {", ".join(valid_types)}')
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None