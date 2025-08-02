from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_
from typing import Optional, List
from .base import BaseRepository
from models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model with domain-specific methods."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return await self.get_by_field("email", email)
    
    async def get_active_users(
        self,
        user_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get active users with optional type filtering."""
        filters = {"is_active": True}
        if user_type:
            filters["user_type"] = user_type
        
        return await self.get_all(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="created_at",
            order_desc=True
        )
    
    async def search_users(
        self,
        search_term: str,
        user_type: Optional[str] = None
    ) -> List[User]:
        """Search users by name or email."""
        query = select(User).where(
            and_(
                User.is_active == True,
                (
                    User.first_name.ilike(f'%{search_term}%') |
                    User.last_name.ilike(f'%{search_term}%') |
                    User.email.ilike(f'%{search_term}%')
                )
            )
        )
        
        if user_type:
            query = query.where(User.user_type == user_type)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_sellers_with_properties(self) -> List[User]:
        """Get sellers who have active properties."""
        return await self.get_all(
            filters={"user_type": "seller"},
            load_relationships=["properties"]
        )
    
    async def get_lawyers_by_specialization(
        self,
        specialization: str
    ) -> List[User]:
        """Get lawyers with specific specialization."""
        # This would typically join with lawyer_profiles table
        # For now, we'll use a basic filter
        return await self.get_all(
            filters={"user_type": "lawyer"},
            load_relationships=["lawyer_profile"]
        )
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Soft delete a user by setting is_active to False."""
        user = await self.update(user_id, is_active=False)
        return user is not None
    
    async def email_exists(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if email is already taken by another user."""
        query = select(User).where(User.email == email)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None 