"""OAuth-only authentication service for handling multiple OAuth providers."""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any
import logging
import json
from datetime import datetime, timezone

from models.user import User, UserLinkedAccount, UserOAuthSession, AuthProvider, UserType
from services.jwt_service import jwt_service
from services.oauth_providers.base import OAuthUserInfo, OAuthTokens
from database.redis_client import redis_client

logger = logging.getLogger(__name__)

class AuthService:
    """OAuth-only authentication service with proper identity resolution."""
    
    def __init__(self):
        pass
    
    # ===== OAuth Authentication =====
    
    async def authenticate_or_create_oauth_user(self, db: Session, provider: str, 
                                              oauth_user_info: OAuthUserInfo,
                                              oauth_tokens: OAuthTokens) -> User:
        """
        Authenticate or create user from OAuth provider.
        Handles identity resolution and account linking.
        """
        try:
            provider_enum = AuthProvider(provider)
            
            # Step 1: Look for existing linked account
            existing_linked_account = db.query(UserLinkedAccount).filter(
                and_(
                    UserLinkedAccount.provider == provider_enum,
                    UserLinkedAccount.provider_user_id == oauth_user_info.provider_user_id
                )
            ).first()
            
            if existing_linked_account:
                # Update existing linked account and create new session
                user = existing_linked_account.user
                await self._update_linked_account(existing_linked_account, oauth_user_info)
                await self._create_oauth_session(db, user.id, existing_linked_account.id, oauth_tokens)
                user.last_login = datetime.now(timezone.utc)
                db.commit()
                logger.info(f"OAuth user {user.email} logged in via {provider}")
                return user
            
            # Step 2: Look for existing user by email
            existing_user = db.query(User).filter(User.email == oauth_user_info.email).first()
            
            if existing_user:
                # Create linked account and OAuth session for existing user
                linked_account = UserLinkedAccount(
                    user_id=existing_user.id,
                    provider=provider_enum,
                    provider_user_id=oauth_user_info.provider_user_id,
                    provider_username=oauth_user_info.username,
                    provider_email=oauth_user_info.email,
                    provider_data=json.dumps(oauth_user_info.raw_data) if oauth_user_info.raw_data else None,
                    verified_at=datetime.now(timezone.utc),
                    is_primary=False  # Not primary since user already exists
                )
                
                db.add(linked_account)
                db.flush()  # Get the ID
                
                # Create OAuth session
                await self._create_oauth_session(db, existing_user.id, linked_account.id, oauth_tokens)
                existing_user.last_login = datetime.now(timezone.utc)
                
                # Update user profile if OAuth has better info
                if oauth_user_info.profile_picture_url and not existing_user.profile_picture_url:
                    existing_user.profile_picture_url = oauth_user_info.profile_picture_url
                if oauth_user_info.email_verified:
                    existing_user.email_verified = True
                
                db.commit()
                logger.info(f"Linked {provider} OAuth to existing user {existing_user.email}")
                return existing_user
            
            # Step 3: Create new user
            new_user = User(
                email=oauth_user_info.email,
                first_name=oauth_user_info.first_name,
                last_name=oauth_user_info.last_name,
                display_name=oauth_user_info.display_name,
                profile_picture_url=oauth_user_info.profile_picture_url,
                is_verified=True,  # OAuth users start verified
                email_verified=oauth_user_info.email_verified,
                last_login=datetime.now(timezone.utc),
                user_type=None  # Will be set after role selection
            )
            
            db.add(new_user)
            db.flush()  # Get user ID
            
            # Create linked account
            linked_account = UserLinkedAccount(
                user_id=new_user.id,
                provider=provider_enum,
                provider_user_id=oauth_user_info.provider_user_id,
                provider_username=oauth_user_info.username,
                provider_email=oauth_user_info.email,
                provider_data=json.dumps(oauth_user_info.raw_data) if oauth_user_info.raw_data else None,
                verified_at=datetime.now(timezone.utc),
                is_primary=True  # First OAuth account is primary
            )
            
            db.add(linked_account)
            db.flush()  # Get the ID
            
            # Create OAuth session
            await self._create_oauth_session(db, new_user.id, linked_account.id, oauth_tokens)
            db.commit()
            
            logger.info(f"Created new OAuth user {new_user.email} via {provider}")
            return new_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to authenticate/create OAuth user: {e}")
            raise ValueError(f"OAuth authentication failed: {str(e)}")
    
    async def _update_linked_account(self, linked_account: UserLinkedAccount, 
                                   user_info: OAuthUserInfo):
        """Update existing linked account with fresh user info."""
        # Update profile data
        linked_account.provider_username = user_info.username
        linked_account.provider_email = user_info.email
        linked_account.provider_data = json.dumps(user_info.raw_data) if user_info.raw_data else None
        linked_account.updated_at = datetime.now(timezone.utc)
    
    async def _create_oauth_session(self, db: Session, user_id: int, linked_account_id: int, tokens: OAuthTokens):
        """Create a new OAuth session for the user."""
        # Deactivate old sessions for this linked account
        db.query(UserOAuthSession).filter(
            and_(
                UserOAuthSession.user_id == user_id,
                UserOAuthSession.linked_account_id == linked_account_id
            )
        ).update({"is_active": False})
        
        # Create new session
        oauth_session = UserOAuthSession(
            user_id=user_id,
            linked_account_id=linked_account_id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_expires_at=tokens.expires_at,
            scopes=tokens.scope,
            last_used_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc).replace(hour=23, minute=59, second=59)  # End of day
        )
        
        db.add(oauth_session)
        return oauth_session
    
    
    # ===== User Management =====
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        try:
            return db.query(User).filter(
                and_(User.id == user_id, User.is_active == True)
            ).first()
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return db.query(User).filter(
                and_(User.email == email, User.is_active == True)
            ).first()
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    def update_user_type(self, db: Session, user_id: int, user_type: str, 
                        phone: Optional[str] = None) -> User:
        """Update user type after OAuth registration."""
        try:
            user = self.get_user_by_id(db, user_id)
            if not user:
                raise ValueError("User not found")
            
            # Convert string to enum
            if user_type == "consumer":
                user.user_type = UserType.CONSUMER
            elif user_type == "agent":
                user.user_type = UserType.AGENT
            elif user_type == "lawyer":
                user.user_type = UserType.LAWYER
            else:
                raise ValueError("Invalid user type")
            
            if phone:
                user.phone = phone
            
            db.commit()
            logger.info(f"User type updated for {user.email}: {user_type}")
            return user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update user type: {e}")
            raise ValueError("Failed to update user information")
    
    # ===== Session Management =====
    
    async def create_user_session(self, user: User) -> Dict[str, Any]:
        """Create JWT tokens and session for user."""
        user_data = {
            "id": user.id,
            "email": user.email,
            "user_type": user.user_type.value if user.user_type else None,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "display_name": user.display_name
        }
        
        # Create JWT tokens
        access_token = jwt_service.create_access_token(user_data)
        refresh_token = jwt_service.create_refresh_token(user_data["id"])
        
        logger.info(f"Creating session check access token for user {access_token}")
        logger.info(f"Creating session check refresh token for user {refresh_token}")
        # Store session in Redis
        session_data = {
            "user_id": user.id,
            "email": user.email,
            "user_type": user.user_type.value if user.user_type else None,
            "login_time": datetime.now(timezone.utc).isoformat(),
            "display_name": user.display_name
        }
        
        await redis_client.set_user_session(user.id, session_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user_data
        }
    
    async def logout_user(self, user_id: int) -> bool:
        """Clear user session."""
        try:
            await redis_client.delete_user_session(user_id)
            logger.info(f"User logged out: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to logout user: {e}")
            return False


# Global auth service instance
auth_service = AuthService()