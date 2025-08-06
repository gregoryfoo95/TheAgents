"""Authentication schemas for OAuth 2.0 and JWT token management."""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from enum import Enum

from .base import BaseResponse
from .user import UserType


class OAuthProvidersResponse(BaseModel):
    """Response schema for available OAuth providers."""
    providers: List[str] = Field(..., description="List of available OAuth providers")


class TokenResponse(BaseModel):
    """Response schema for JWT tokens."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: Optional[str] = Field(None, description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")
    refresh_expires_in: Optional[int] = Field(None, description="Refresh token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    refresh_token: str = Field(..., description="Valid refresh token")


class UserTypeSelectionData(BaseModel):
    """Schema for user type selection after OAuth authentication."""
    user_type: UserType = Field(..., description="Type of user account")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="User's phone number")


class AuthCallbackResponse(BaseModel):
    """Response schema for OAuth callback."""
    success: bool = Field(..., description="Whether authentication was successful")
    message: str = Field(..., description="Status message")
    tokens: Optional[TokenResponse] = Field(None, description="JWT tokens if successful")
    user: Optional[Dict[str, Any]] = Field(None, description="User information if successful")


class OAuthUserInfo(BaseModel):
    """Schema for normalized OAuth user information."""
    id: str = Field(..., description="OAuth provider user ID")
    email: EmailStr = Field(..., description="User email")
    first_name: str = Field(..., description="User first name")
    last_name: str = Field(..., description="User last name")
    full_name: Optional[str] = Field(None, description="User full name")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    email_verified: bool = Field(default=False, description="Whether email is verified")


class SessionInfo(BaseModel):
    """Schema for user session information."""
    active_sessions: int = Field(..., description="Number of active sessions")
    last_login: Optional[str] = Field(None, description="Last login timestamp")


# Legacy schemas for backward compatibility during migration
class LegacyToken(BaseModel):
    """Legacy token schema for backward compatibility."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
