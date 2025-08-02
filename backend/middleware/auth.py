from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from utilities.database import get_async_db
from services.user_service import UserService
from schemas.user import User as UserSchema

# Create security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> Optional[UserSchema]:
    """
    Get current user from JWT token (optional).
    Returns None if no token or invalid token.
    """
    if not credentials:
        return None
    
    try:
        user_service = UserService(db)
        user = await user_service.verify_token(credentials.credentials)
        return user
    except Exception:
        return None


async def get_current_active_user(
    current_user: Optional[UserSchema] = Depends(get_current_user)
) -> UserSchema:
    """
    Get current active user (required authentication).
    Raises 401 if not authenticated or user inactive.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def require_seller(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be a seller.
    Raises 403 if user is not a seller.
    """
    if current_user.user_type != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action"
        )
    
    return current_user


async def require_buyer(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be a buyer.
    Raises 403 if user is not a buyer.
    """
    if current_user.user_type != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers can perform this action"
        )
    
    return current_user


async def require_lawyer(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be a lawyer.
    Raises 403 if user is not a lawyer.
    """
    if current_user.user_type != "lawyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only lawyers can perform this action"
        )
    
    return current_user


async def require_buyer_or_seller(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be either a buyer or seller.
    Raises 403 if user is not a buyer or seller.
    """
    if current_user.user_type not in ["buyer", "seller"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only buyers and sellers can perform this action"
        )
    
    return current_user


async def require_admin(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be an admin.
    Raises 403 if user is not an admin.
    """
    # For now, we don't have admin users defined in the schema
    # This is a placeholder for future admin functionality
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    ) 