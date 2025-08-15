from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from models.property import PropertyType, PropertyStatus, BookingStatus

# Property schemas
class PropertyBase(BaseModel):
    title: str
    description: Optional[str]
    property_type: PropertyType
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    bedrooms: int
    bathrooms: int
    square_feet: Optional[int]
    rent_amount: Decimal
    security_deposit: Optional[Decimal]
    amenities: Optional[Dict[str, Any]]
    features: Optional[Dict[str, Any]]

class PropertyCreate(PropertyBase):
    @validator('rent_amount')
    def validate_rent_amount(cls, v):
        if v <= 0:
            raise ValueError('Rent amount must be positive')
        return v

class PropertyUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    property_type: Optional[PropertyType]
    bedrooms: Optional[int]
    bathrooms: Optional[int]
    square_feet: Optional[int]
    rent_amount: Optional[Decimal]
    security_deposit: Optional[Decimal]
    status: Optional[PropertyStatus]
    amenities: Optional[Dict[str, Any]]
    features: Optional[Dict[str, Any]]

class PropertyResponse(PropertyBase):
    id: int
    owner_id: int
    status: PropertyStatus
    is_active: bool
    available_from: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Booking schemas
class BookingCreate(BaseModel):
    property_id: int
    start_date: datetime
    end_date: datetime
    notes: Optional[str]

class BookingResponse(BaseModel):
    id: int
    property_id: int
    tenant_id: int
    start_date: datetime
    end_date: datetime
    monthly_rent: Decimal
    security_deposit: Optional[Decimal]
    status: BookingStatus
    notes: Optional[str]
    lawyer_id: Optional[int]
    assigned_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True