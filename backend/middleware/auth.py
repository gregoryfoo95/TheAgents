from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from utilities.database import get_async_db
from services.user_service import UserService
from services.jwt_service import jwt_service
from schemas.user import User as UserSchema

import logging

logger = logging.getLogger(__name__)

# Create security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> Optional[UserSchema]:
    """
    Get current user from JWT token (optional).
    Returns None if no token or invalid token.
    First checks HTTP-only cookies, then falls back to Authorization header.
    """
    access_token = None
    
    # First try to get token from HTTP-only cookie
    access_token = request.cookies.get("access_token")
    logger.info(f"get_current_user called with cookie token: {access_token is not None}")
    
    # Fall back to Authorization header if no cookie
    if not access_token and credentials:
        access_token = credentials.credentials
        logger.info(f"Using Authorization header token: {access_token is not None}")
    
    if not access_token:
        logger.info("No access token found in cookies or headers")
        return None

    try:
        # Verify JWT token
        payload = jwt_service.verify_token(access_token, token_type="access")

        # Check if token is blacklisted
        if jwt_service.is_token_blacklisted(access_token):
            return None

        # Get user from database using token payload
        logger.info(f"Token payload: {payload}")
        user_id = int(payload.get("sub"))
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)

        return user
    except HTTPException:
        # JWT service raises HTTPException for invalid tokens
        return None
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


async def require_agent(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be an agent.
    Raises 403 if user is not an agent.
    """
    if current_user.user_type != "agent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only agents can perform this action"
        )

    return current_user


async def require_consumer(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be a consumer.
    Raises 403 if user is not a consumer.
    """
    if current_user.user_type != "consumer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers can perform this action"
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


async def require_consumer_or_agent(
    current_user: UserSchema = Depends(get_current_active_user)
) -> UserSchema:
    """
    Require user to be either a consumer or agent.
    Raises 403 if user is not a consumer or agent.
    """
    if current_user.user_type not in ["consumer", "agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only consumers and agents can perform this action"
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
