from datetime import datetime, timedelta
from typing import Optional, List
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import bcrypt

from repositories.user import UserRepository
from schemas.user import UserCreate, UserUpdate, UserLogin, Token, User as UserSchema
from models.user import User
from utilities.config import get_settings
from utilities.redis import redis_client, cache_result

settings = get_settings()


class UserService:
    """Service layer for user-related business logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def create_user(self, user_data: UserCreate) -> UserSchema:
        """Create a new user with validation and password hashing."""
        # Check if email already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self._hash_password(user_data.password)
        
        # Create user
        user_dict = user_data.model_dump(exclude={'password'})
        user_dict['password_hash'] = hashed_password
        
        user = await self.user_repo.create(**user_dict)
        
        # Clear cache for user lists
        await self._invalidate_user_cache()
        
        return UserSchema.model_validate(user)
    
    async def authenticate_user(self, login_data: UserLogin) -> Token:
        """Authenticate user and return JWT token."""
        user = await self.user_repo.get_by_email(login_data.email)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not self._verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token = self._create_access_token(
            data={"sub": user.email, "user_id": user.id, "user_type": user.user_type}
        )
        
        # Cache user session
        await redis_client.set_json(
            f"user_session:{user.id}",
            {
                "user_id": user.id,
                "email": user.email,
                "user_type": user.user_type,
                "login_time": datetime.utcnow().isoformat()
            },
            expire=settings.access_token_expire_minutes * 60
        )
        
        return Token(access_token=access_token)
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserSchema]:
        """Get user by ID with caching."""
        cache_key = f"user:{user_id}"
        
        # Try cache first
        cached_user = await redis_client.get_json(cache_key)
        if cached_user:
            return UserSchema(**cached_user)
        
        # Get from database
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        user_schema = UserSchema.model_validate(user)
        
        # Cache for 15 minutes
        await redis_client.set_json(cache_key, user_schema.model_dump(), expire=900)
        
        return user_schema
    
    async def get_user_by_email(self, email: str) -> Optional[UserSchema]:
        """Get user by email."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        return UserSchema.model_validate(user)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserSchema]:
        """Update user information with validation."""
        # Check if user exists
        existing_user = await self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != existing_user.email:
            if await self.user_repo.email_exists(user_data.email, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
        
        # Update user
        update_data = user_data.model_dump(exclude_unset=True)
        updated_user = await self.user_repo.update(user_id, **update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Invalidate caches
        await self._invalidate_user_cache(user_id)
        
        return UserSchema.model_validate(updated_user)
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        success = await self.user_repo.deactivate_user(user_id)
        if success:
            await self._invalidate_user_cache(user_id)
        return success
    
    async def get_users(
        self,
        user_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[UserSchema]:
        """Get list of users with optional filtering."""
        users = await self.user_repo.get_active_users(
            user_type=user_type,
            skip=skip,
            limit=limit
        )
        return [UserSchema.model_validate(user) for user in users]
    
    async def search_users(
        self,
        search_term: str,
        user_type: Optional[str] = None
    ) -> List[UserSchema]:
        """Search users by name or email."""
        users = await self.user_repo.search_users(search_term, user_type)
        return [UserSchema.model_validate(user) for user in users]
    
    async def verify_token(self, token: str) -> Optional[UserSchema]:
        """Verify JWT token and return user."""
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                return None
            
            # Check if session exists in Redis
            session_data = await redis_client.get_json(f"user_session:{user_id}")
            if not session_data:
                return None
            
            # Get user
            user = await self.get_user_by_email(email)
            if user is None or not user.is_active:
                return None
            
            return user
            
        except JWTError:
            return None
    
    async def logout_user(self, user_id: int) -> bool:
        """Logout user by removing session from Redis."""
        return await redis_client.delete(f"user_session:{user_id}") > 0
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _create_access_token(self, data: dict) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
    
    async def _invalidate_user_cache(self, user_id: Optional[int] = None) -> None:
        """Invalidate user-related caches."""
        if user_id:
            await redis_client.delete(f"user:{user_id}")
            await redis_client.delete(f"user_session:{user_id}")
        
        # Invalidate general user list caches
        await redis_client.delete("users:active")
        await redis_client.delete("users:sellers")
        await redis_client.delete("users:buyers")
        await redis_client.delete("users:lawyers") 