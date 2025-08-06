from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base import BaseResponse, PaginatedResponse
from .user import User


class AddressBase(BaseModel):
    """Base schema for property addresses."""
    street_address: str = Field(..., min_length=1, max_length=500, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=2, max_length=50, description="State")
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP code")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude")

    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Validate ZIP code format."""
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) not in [5, 9]:
            raise ValueError('ZIP code must be 5 or 9 digits')
        return v

    @validator('state')
    def validate_state(cls, v):
        """Validate state format."""
        return v.strip().upper()


class Address(AddressBase, BaseResponse):
    """Address response schema."""
    id: int = Field(..., description="Address ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = ConfigDict(from_attributes=True)


class PropertyImageBase(BaseModel):
    """Base schema for property images."""
    image_url: str = Field(..., min_length=1, max_length=500, description="Image URL")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text for image")
    is_primary: bool = Field(False, description="Is primary image")
    display_order: int = Field(0, description="Display order")


class PropertyImage(PropertyImageBase, BaseResponse):
    """Property image response schema."""
    id: int = Field(..., description="Image ID")
    property_id: int = Field(..., description="Property ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


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
    # Address fields for backward compatibility in create/update
    address: str = Field(..., min_length=1, max_length=500, description="Property address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=2, max_length=50, description="State")
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP code")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude")

    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Validate ZIP code format."""
        digits_only = ''.join(filter(str.isdigit, v))
        if len(digits_only) not in [5, 9]:
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
    status: Optional[PropertyStatus] = Field(None, description="Property status")
    # Note: Address updates should be handled through separate endpoint


class Property(BaseResponse):
    """Property response schema."""
    id: int = Field(..., description="Property ID")
    seller_id: int = Field(..., description="Seller ID")
    address_id: int = Field(..., description="Address ID")
    title: str = Field(..., description="Property title")
    description: Optional[str] = Field(None, description="Property description")
    property_type: PropertyType = Field(..., description="Type of property")
    price: Decimal = Field(..., description="Property price")
    ai_estimated_price: Optional[Decimal] = Field(None, description="AI estimated price")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[int] = Field(None, description="Number of bathrooms")
    square_feet: Optional[int] = Field(None, description="Square footage")
    status: PropertyStatus = Field(..., description="Property status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Nested objects
    seller: Optional[User] = Field(None, description="Property seller")
    address: Optional[Address] = Field(None, description="Property address")
    images: Optional[List[PropertyImage]] = Field(default=[], description="Property images")
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
