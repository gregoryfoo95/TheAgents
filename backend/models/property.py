from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List

from utilities.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    street_address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    properties = relationship("Property", back_populates="address")

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, city='{self.city}', state='{self.state}')>"

    @property
    def full_address(self) -> str:
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(Integer, ForeignKey("properties.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Integer, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    property = relationship("Property", back_populates="images")

    def __repr__(self) -> str:
        return f"<PropertyImage(id={self.id}, property_id={self.property_id})>"

class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    address_id: Mapped[int] = mapped_column(Integer, ForeignKey("addresses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    property_type: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    ai_estimated_price: Mapped[float] = mapped_column(Float, nullable=True)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=True)
    square_feet: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='active')
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    seller = relationship("User", back_populates="properties")
    address = relationship("Address", back_populates="properties")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan")
    features = relationship("PropertyFeature", back_populates="property", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Property(id={self.id}, title='{self.title}', price=${self.price})>"

    @property
    def formatted_price(self) -> str:
        return f"${self.price:,.2f}"

    @property
    def price_per_sqft(self) -> float:
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