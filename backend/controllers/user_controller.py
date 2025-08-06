from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from utilities.database import get_async_db
from services.user_service import UserService
from schemas.user import UserCreate, UserUpdate, User as UserSchema
from schemas.base import SuccessResponse, ErrorResponse
from middleware.auth import get_current_user, get_current_active_user

user_router = APIRouter(prefix="/api/users", tags=["users"])



@user_router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user"
)
async def get_current_user_profile(
    current_user: UserSchema = Depends(get_current_active_user)
):
    """Get current user's profile."""
    return current_user


@user_router.put(
    "/me",
    response_model=UserSchema,
    summary="Update current user profile",
    description="Update the profile information of the currently authenticated user"
)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update current user's profile."""
    try:
        user_service = UserService(db)
        updated_user = await user_service.update_user(current_user.id, user_data)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@user_router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Get user by ID",
    description="Get public profile information for a specific user"
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserSchema = Depends(get_current_user)  # Optional authentication
):
    """Get user by ID (public profile)."""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@user_router.get(
    "/",
    response_model=List[UserSchema],
    summary="Get users list",
    description="Get a list of users with optional filtering by type"
)
async def get_users(
    user_type: Optional[str] = Query(None, description="Filter by user type (consumer, agent, lawyer)"),
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of users to return"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get list of users (requires authentication)."""
    try:
        user_service = UserService(db)
        users = await user_service.get_users(
            user_type=user_type,
            skip=skip,
            limit=limit
        )
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@user_router.get(
    "/search/",
    response_model=List[UserSchema],
    summary="Search users",
    description="Search users by name or email"
)
async def search_users(
    q: str = Query(..., min_length=2, description="Search term (name or email)"),
    user_type: Optional[str] = Query(None, description="Filter by user type"),
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Search users by name or email."""
    try:
        user_service = UserService(db)
        users = await user_service.search_users(
            search_term=q,
            user_type=user_type
        )
        return users
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@user_router.delete(
    "/me",
    response_model=SuccessResponse,
    summary="Deactivate current user account",
    description="Deactivate the currently authenticated user's account"
)
async def deactivate_current_user(
    current_user: UserSchema = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Deactivate current user's account."""
    try:
        user_service = UserService(db)
        success = await user_service.deactivate_user(current_user.id)

        if success:
            return SuccessResponse(message="Account deactivated successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate account"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate account: {str(e)}"
        )
