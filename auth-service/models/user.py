from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship
from enum import Enum
import uuid

class Base(DeclarativeBase):
    pass

class UserType(str, Enum):
    CONSUMER = "consumer"
    AGENT = "agent" 
    LAWYER = "lawyer"

class AuthProvider(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"

class User(Base):
    """Primary user entity - provider-agnostic"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core user information (populated from first OAuth provider or registration)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    user_type = Column(SQLEnum(UserType), nullable=True)  # Set after registration
    
    # Profile
    display_name = Column(String(200), nullable=True)  # Optional display name
    profile_picture_url = Column(String(500), nullable=True)
    bio = Column(String(1000), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    linked_accounts = relationship("UserLinkedAccount", back_populates="user", cascade="all, delete-orphan")
    oauth_sessions = relationship("UserOAuthSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', user_type='{self.user_type}')>"

class UserLinkedAccount(Base):
    """OAuth provider accounts permanently linked to a user - for identity purposes"""
    __tablename__ = "user_linked_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # OAuth provider information
    provider = Column(SQLEnum(AuthProvider), nullable=False, index=True)
    provider_user_id = Column(String(100), nullable=False, index=True)  # Provider's ID for this user
    provider_username = Column(String(100), nullable=True)  # Username/handle at provider
    provider_email = Column(String(255), nullable=True)  # Email at provider (might differ from main email)
    
    # Provider-specific profile data
    provider_data = Column(String(2000), nullable=True)  # JSON string with provider-specific info
    
    # Account linking metadata
    verified_at = Column(DateTime(timezone=True), nullable=True)  # When this account was verified
    is_primary = Column(Boolean, default=False, nullable=False)  # Is this the primary OAuth account for the user?
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="linked_accounts")
    
    # Unique constraint: one account per provider per provider_user_id
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='unique_linked_account'),
    )
    
    def __repr__(self):
        return f"<UserLinkedAccount(user_id={self.user_id}, provider='{self.provider}', provider_user_id='{self.provider_user_id}')>"

class UserOAuthSession(Base):
    """OAuth session data for API calls to providers - temporary/renewable"""
    __tablename__ = "user_oauth_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    linked_account_id = Column(Integer, ForeignKey("user_linked_accounts.id", ondelete="CASCADE"), nullable=False)
    
    # OAuth tokens (should be encrypted in production)
    access_token = Column(String(1000), nullable=True)
    refresh_token = Column(String(1000), nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Session metadata
    scopes = Column(String(500), nullable=True)  # OAuth scopes granted
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # When to clean up this session
    
    # Relationships
    user = relationship("User", back_populates="oauth_sessions")
    linked_account = relationship("UserLinkedAccount")
    
    def __repr__(self):
        return f"<UserOAuthSession(user_id={self.user_id}, linked_account_id={self.linked_account_id}, active={self.is_active})>"