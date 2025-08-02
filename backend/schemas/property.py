from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base import BaseResponse, PaginatedResponse
from .user import User


class PropertyType(str, Enum):
    """Property type enumeration."""
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    LAND = "land"
    COMMERCIAL = "commercial"


class PropertyStatus(str, Enum):
    """Property status enumeration."""
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"


class PropertyFeatureBase(BaseModel):
    """Base schema for property features."""
    feature_name: str = Field(..., min_length=1, max_length=100, description="Feature name")
    feature_value: Optional[str] = Field(None, max_length=255, description="Feature value")


class PropertyFeature(PropertyFeatureBase, BaseResponse):
    """Property feature response schema."""
    id: int = Field(..., description="Feature ID")
    property_id: int = Field(..., description="Property ID")
    
    model_config = ConfigDict(from_attributes=True)


class PropertyBase(BaseModel):
    """Base property schema with common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    property_type: PropertyType = Field(..., description="Type of property")
    price: Decimal = Field(..., gt=0, description="Property price")
    bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bathrooms")
    square_feet: Optional[int] = Field(None, gt=0, description="Square footage")
    address: str = Field(..., min_length=1, max_length=500, description="Property address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=2, max_length=50, description="State")
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP code")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude")
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Validate ZIP code format."""
        # Remove any non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) not in [5, 9]:  # US ZIP codes
            raise ValueError('ZIP code must be 5 or 9 digits')
        return v
    
    @validator('state')
    def validate_state(cls, v):
        """Validate state format."""
        return v.strip().upper()


class PropertyCreate(PropertyBase):
    """Schema for creating a new property."""
    features: Optional[List[PropertyFeatureBase]] = Field(default=[], description="Property features")


class PropertyUpdate(BaseModel):
    """Schema for updating property information."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    property_type: Optional[PropertyType] = Field(None, description="Type of property")
    price: Optional[Decimal] = Field(None, gt=0, description="Property price")
    bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bathrooms")
    square_feet: Optional[int] = Field(None, gt=0, description="Square footage")
    address: Optional[str] = Field(None, min_length=1, max_length=500, description="Property address")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City")
    state: Optional[str] = Field(None, min_length=2, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, min_length=5, max_length=10, description="ZIP code")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude")
    status: Optional[PropertyStatus] = Field(None, description="Property status")
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Validate ZIP code format."""
        if v is None:
            return v
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) not in [5, 9]:
            raise ValueError('ZIP code must be 5 or 9 digits')
        return v
    
    @validator('state')
    def validate_state(cls, v):
        """Validate state format."""
        if v is None:
            return v
        return v.strip().upper()


class Property(PropertyBase, BaseResponse):
    """Property response schema."""
    id: int = Field(..., description="Property ID")
    seller_id: int = Field(..., description="Seller ID")
    ai_estimated_price: Optional[Decimal] = Field(None, description="AI estimated price")
    status: PropertyStatus = Field(..., description="Property status")
    images: Optional[List[str]] = Field(default=[], description="Property image URLs")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Nested objects
    seller: Optional[User] = Field(None, description="Property seller")
    features: Optional[List[PropertyFeature]] = Field(default=[], description="Property features")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }
    )


class PropertyFilters(BaseModel):
    """Schema for property filtering."""
    property_type: Optional[PropertyType] = Field(None, description="Filter by property type")
    min_price: Optional[Decimal] = Field(None, gt=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, gt=0, description="Maximum price")
    bedrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, ge=0, le=20, description="Number of bathrooms")
    min_square_feet: Optional[int] = Field(None, gt=0, description="Minimum square footage")
    max_square_feet: Optional[int] = Field(None, gt=0, description="Maximum square footage")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City")
    state: Optional[str] = Field(None, min_length=2, max_length=50, description="State")
    zip_code: Optional[str] = Field(None, min_length=5, max_length=10, description="ZIP code")
    status: Optional[PropertyStatus] = Field(PropertyStatus.ACTIVE, description="Property status")
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        """Validate max price is greater than min price."""
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v <= values['min_price']:
                raise ValueError('Maximum price must be greater than minimum price')
        return v
    
    @validator('max_square_feet')
    def validate_square_feet_range(cls, v, values):
        """Validate max square feet is greater than min square feet."""
        if v is not None and 'min_square_feet' in values and values['min_square_feet'] is not None:
            if v <= values['min_square_feet']:
                raise ValueError('Maximum square feet must be greater than minimum square feet')
        return v


class PropertyListResponse(PaginatedResponse[Property]):
    """Paginated property list response."""
    pass


class PropertyImageUpload(BaseModel):
    """Schema for property image upload response."""
    property_id: int = Field(..., description="Property ID")
    image_urls: List[str] = Field(..., description="Uploaded image URLs")
    total_images: int = Field(..., description="Total number of images for property")
    
    model_config = ConfigDict(from_attributes=True) 