from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, ARRAY, func
from sqlalchemy.orm import relationship
from datetime import datetime
from utilities.database import Base
import enum


class Property(Base):
    """Property model for real estate listings."""
    
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    property_type = Column(String(50), nullable=False)
    price = Column(Float, nullable=False)
    ai_estimated_price = Column(Float)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_feet = Column(Integer)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(10), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String(20), default='active')  # 'active', 'pending', 'sold', 'withdrawn'
    images = Column(ARRAY(Text))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    seller = relationship("User", back_populates="properties")
    features = relationship("PropertyFeature", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Property(id={self.id}, address='{self.address}', price=${self.price})>"
    
    # @property
    def address_full(self) -> str:
        """Get full formatted address."""
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"
    
    # @property
    def formatted_price(self) -> str:
        """Get formatted price."""
        return f"${self.price:,.2f}"
    
    # @property
    def price_per_sqft(self) -> float:
        """Calculate price per square foot."""
        if self.square_feet and self.square_feet > 0:
            return self.price / self.square_feet
        return 0.0
    
    @property
    def is_available(self) -> bool:
        """Check if property is available for viewing/purchase."""
        return self.status == 'active'


class PropertyFeature(Base):
    """Property features/amenities model."""
    
    __tablename__ = "property_features"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    feature_name = Column(String(100), nullable=False)
    feature_value = Column(String(255))
    
    # Relationships
    property = relationship("Property", back_populates="features")
    
    def __repr__(self) -> str:
        return f"<PropertyFeature(id={self.id}, name='{self.feature_name}', value='{self.feature_value}')>" 