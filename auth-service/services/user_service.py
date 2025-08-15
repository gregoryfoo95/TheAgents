from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import bcrypt
import logging
from datetime import datetime, timezone

from models.user import User, UserType
from services.jwt_service import jwt_service
from database.redis_client import redis_client

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        pass
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_user(self, db: Session, email: str, password: str, 
                   first_name: str, last_name: str, user_type: UserType) -> User:
        """Create new user"""
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == email).first()
            
            if existing_user:
                raise ValueError("Email already registered")
            
            # Hash password
            hashed_password = self.hash_password(password)
            
            # Create user
            user = User(
                email=email,
                hashed_password=hashed_password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"User created: {user.email}")
            return user
            
        except ValueError:
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise ValueError("Failed to create user")
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        try:
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                logger.warning(f"User not found: {email}")
                return None
            
            if not user.is_active:
                logger.warning(f"Inactive user login attempt: {email}")
                return None
            
            if not user.hashed_password:
                logger.warning(f"OAuth user tried password login: {email}")
                return None
            
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            db.commit()
            
            logger.info(f"User authenticated: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
            return user
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user = db.query(User).filter(User.email == email, User.is_active == True).first()
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    async def login_user(self, db: Session, email: str, password: str) -> dict:
        """Login user and create session"""
        user = self.authenticate_user(db, email, password)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Prepare user data for JWT
        user_data = {
            "id": user.id,
            "email": user.email,
            "user_type": user.user_type.value,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
        
        # Create JWT tokens
        access_token = jwt_service.create_access_token(user_data)
        refresh_token = jwt_service.create_refresh_token(user.id)
        
        # Store session in Redis
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "user_type": user.user_type.value,
            "login_time": datetime.now(timezone.utc).isoformat()
        }
        
        await redis_client.set_user_session(user.id, session_data)
        await redis_client.cache_user_data(user.id, user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_data
        }
    
    async def logout_user(self, user_id: int) -> bool:
        """Logout user and clear session"""
        try:
            await redis_client.delete_user_session(user_id)
            logger.info(f"User logged out: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to logout user: {e}")
            return False
    
    def get_or_create_oauth_user(self, db: Session, oauth_provider: str, oauth_id: str, 
                                email: str, first_name: str, last_name: str, 
                                profile_picture_url: Optional[str] = None) -> User:
        """Get existing OAuth user or create new one"""
        try:
            # Check if user already exists by OAuth ID
            existing_user = db.query(User).filter(
                User.oauth_provider == oauth_provider,
                User.oauth_id == oauth_id
            ).first()
            
            if existing_user:
                # Update last login
                existing_user.last_login = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"Existing OAuth user logged in: {existing_user.email}")
                return existing_user
            
            # Check if user exists by email (different OAuth provider or converted account)
            existing_email_user = db.query(User).filter(User.email == email).first()
            if existing_email_user:
                # Link OAuth account to existing user
                if oauth_provider == "google":
                    existing_email_user.google_id = oauth_id
                existing_email_user.oauth_provider = oauth_provider
                existing_email_user.oauth_id = oauth_id
                if profile_picture_url:
                    existing_email_user.profile_picture_url = profile_picture_url
                existing_email_user.last_login = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"Linked OAuth to existing user: {existing_email_user.email}")
                return existing_email_user
            
            # Create new OAuth user (without user_type for role selection)
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                user_type=None,  # Will be set after role selection
                oauth_provider=oauth_provider,
                oauth_id=oauth_id,
                profile_picture_url=profile_picture_url,
                is_verified=True,  # OAuth users are pre-verified
                last_login=datetime.now(timezone.utc)
            )
            
            # Set provider-specific fields
            if oauth_provider == "google":
                user.google_id = oauth_id
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New OAuth user created: {user.email}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to get/create OAuth user: {e}")
            raise ValueError("Failed to process OAuth user")
    
    def update_user_type_and_info(self, db: Session, user_id: int, user_type: str, 
                                 phone: Optional[str] = None) -> User:
        """Update user type and additional info after OAuth login"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Map string to enum
            user_type_enum = None
            if user_type == "consumer":
                user_type_enum = UserType.HOMEOWNER  # Map consumer to homeowner
            elif user_type == "agent":
                user_type_enum = UserType.TENANT  # Map agent to tenant
            elif user_type == "lawyer":
                user_type_enum = UserType.LAWYER
            else:
                raise ValueError("Invalid user type")
            
            user.user_type = user_type_enum
            db.commit()
            db.refresh(user)
            
            logger.info(f"User type updated for {user.email}: {user_type}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update user type: {e}")
            raise ValueError("Failed to update user information")

# Global user service instance
user_service = UserService()