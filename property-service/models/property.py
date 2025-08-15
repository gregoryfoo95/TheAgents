from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, DeclarativeBase
from enum import Enum

class Base(DeclarativeBase):
    pass

class PropertyType(str, Enum):
    APARTMENT = "apartment"
    HOUSE = "house"
    CONDO = "condo"
    STUDIO = "studio"
    TOWNHOUSE = "townhouse"

class PropertyStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, nullable=False, index=True)  # Reference to User from auth service
    
    # Basic property information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    property_type = Column(SQLEnum(PropertyType), nullable=False)
    
    # Location
    address = Column(String(300), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    country = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    
    # Property details
    bedrooms = Column(Integer, nullable=False)
    bathrooms = Column(Integer, nullable=False)
    square_feet = Column(Integer, nullable=True)
    
    # Pricing
    rent_amount = Column(DECIMAL(10, 2), nullable=False)
    security_deposit = Column(DECIMAL(10, 2), nullable=True)
    
    # Status and availability
    status = Column(SQLEnum(PropertyStatus), default=PropertyStatus.AVAILABLE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    available_from = Column(DateTime(timezone=True), nullable=True)
    
    # Additional features and amenities
    amenities = Column(JSONB, nullable=True)  # {"parking": true, "pool": true, "gym": false}
    features = Column(JSONB, nullable=True)   # {"furnished": true, "pet_friendly": false}
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property(id={self.id}, title='{self.title}', owner_id={self.owner_id})>"

class PropertyImage(Base):
    __tablename__ = "property_images"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    
    # Image metadata
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    property = relationship("Property", back_populates="images")
    
    def __repr__(self):
        return f"<PropertyImage(id={self.id}, property_id={self.property_id}, filename='{self.filename}')>"

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(Integer, nullable=False, index=True)  # Reference to User from auth service
    
    # Booking details
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    monthly_rent = Column(DECIMAL(10, 2), nullable=False)
    security_deposit = Column(DECIMAL(10, 2), nullable=True)
    
    # Status and notes
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Legal assignment
    lawyer_id = Column(Integer, nullable=True, index=True)  # Reference to User (lawyer) from auth service
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    property = relationship("Property", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, property_id={self.property_id}, tenant_id={self.tenant_id}, status='{self.status}')>"