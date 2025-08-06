from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

from .base import BaseResponse


class UserType(str, Enum):
    """User type enumeration."""
    CONSUMER = "consumer"
    AGENT = "agent"
    LAWYER = "lawyer"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="User's phone number")
    user_type: Optional[UserType] = Field(None, description="Type of user account (nullable for first-time selection)")

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate names contain only letters, spaces, hyphens, and apostrophes."""
        if not v.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValueError('Names must contain only letters, spaces, hyphens, and apostrophes')
        return v.strip().title()

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must contain 10-15 digits')
        return v


class UserCreate(UserBase):
    """Schema for creating a new OAuth user."""
    oauth_provider: str = Field(..., description="OAuth provider (google, facebook, etc.)")
    oauth_id: str = Field(..., description="OAuth provider user ID")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="User's phone number")
    user_type: Optional[UserType] = Field(None, description="User type (consumer/agent/lawyer)")

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate names contain only letters, spaces, hyphens, and apostrophes."""
        if v is None:
            return v
        if not v.replace(' ', '').replace('-', '').replace("'", '').isalpha():
            raise ValueError('Names must contain only letters, spaces, hyphens, and apostrophes')
        return v.strip().title()

    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must contain 10-15 digits')
        return v


class User(UserBase, BaseResponse):
    """Schema for user response."""
    id: int = Field(..., description="User's unique identifier")
    oauth_provider: Optional[str] = Field(None, description="OAuth provider")
    oauth_id: Optional[str] = Field(None, description="OAuth provider user ID")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL")
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


