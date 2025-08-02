from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, func
from sqlalchemy.orm import relationship
from datetime import datetime
from utilities.database import Base
import enum


class User(Base):
    """User model for buyers, sellers, and lawyers."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    user_type = Column(String(20), nullable=False)  # 'buyer', 'seller', 'lawyer'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    properties = relationship("Property", back_populates="seller", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', user_type='{self.user_type}')>"
    
    # @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}" 