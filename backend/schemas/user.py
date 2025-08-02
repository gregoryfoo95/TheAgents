from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

from .base import BaseResponse


class UserType(str, Enum):
    """User type enumeration."""
    BUYER = "buyer"
    SELLER = "seller"
    LAWYER = "lawyer"


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="User's phone number")
    user_type: UserType = Field(..., description="Type of user account")
    
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
    """Schema for creating a new user."""
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=128,
        description="User's password (min 8 characters)"
    )
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                'Password must contain at least one uppercase letter, '
                'one lowercase letter, one digit, and one special character'
            )
        
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="User's phone number")
    
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
    is_active: bool = Field(..., description="Whether the user account is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=1, description="User's password")


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Schema for token payload data."""
    email: Optional[str] = Field(None, description="User's email from token") 