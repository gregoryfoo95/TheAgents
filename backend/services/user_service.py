from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from repositories.user import UserRepository
from schemas.user import UserUpdate, User as UserSchema
from utilities.config import get_settings
from utilities.redis import redis_client

settings = get_settings()


class UserService:
    """Service layer for user-related business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def create_oauth_user(
        self,
        oauth_provider: str,
        oauth_id: str,
        email: str,
        first_name: str,
        last_name: str,
        profile_picture_url: Optional[str] = None,
        user_type: Optional[str] = None
    ) -> UserSchema:
        """Create a new OAuth user."""
        # Create user data dict
        user_data = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "oauth_provider": oauth_provider,
            "oauth_id": oauth_id,
            "profile_picture_url": profile_picture_url,
            "user_type": user_type,
            "is_active": True
        }

        user = await self.user_repo.create(**user_data)

        # Clear cache for user lists
        await self._invalidate_user_cache()

        return UserSchema.model_validate(user)

    async def get_or_create_oauth_user(
        self,
        oauth_provider: str,
        oauth_id: str,
        email: str,
        first_name: str,
        last_name: str,
        profile_picture_url: Optional[str] = None
    ) -> UserSchema:
        """Get existing OAuth user or create new one."""
        # Try to find existing user by OAuth ID and provider
        user = await self.user_repo.get_by_oauth_provider_and_id(oauth_provider, oauth_id)

        if user:
            # Update profile picture if provided
            if (profile_picture_url is not None and
                    user.profile_picture_url != profile_picture_url):  # type: ignore
                user_id: int = user.id  # type: ignore
                user = await self.user_repo.update(
                    user_id,
                    profile_picture_url=profile_picture_url
                )
            return UserSchema.model_validate(user)

        # Check if user exists with same email (different OAuth provider)
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {email} already exists with different authentication method")

        # Create new OAuth user with null user_type for role selection
        return await self.create_oauth_user(
            oauth_provider=oauth_provider,
            oauth_id=oauth_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            profile_picture_url=profile_picture_url,
            user_type=None  # Null type for first-time role selection
        )

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

    async def update_user(
            self,
            user_id: int,
            user_data: UserUpdate) -> Optional[UserSchema]:
        """Update user information with validation."""
        # Check if user exists
        existing_user = await self.user_repo.get_by_id(user_id)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Check email uniqueness if email is being updated
        if user_data.email is not None and user_data.email != existing_user.email:  # type: ignore
            email_check = await self.user_repo.get_by_email(user_data.email)
            if email_check is not None and email_check.id != user_id:  # type: ignore
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

    async def update_user_type_and_info(
        self,
        user_id: int,
        user_type: str,
        phone: Optional[str] = None
    ) -> UserSchema:
        """Update user type and additional information for OAuth users."""
        update_data = {"user_type": user_type}
        if phone:
            update_data["phone"] = phone

        updated_user = await self.user_repo.update(user_id, **update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Invalidate caches
        await self._invalidate_user_cache(user_id)

        return UserSchema.model_validate(updated_user)

    async def _invalidate_user_cache(
            self, user_id: Optional[int] = None) -> None:
        """Invalidate user-related caches."""
        if user_id:
            await redis_client.delete(f"user:{user_id}")

        # Invalidate general user list caches
        await redis_client.delete("users:active")
        await redis_client.delete("users:agents")
        await redis_client.delete("users:consumers")
        await redis_client.delete("users:lawyers")
