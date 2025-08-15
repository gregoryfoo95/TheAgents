"""Authentication middleware for protecting routes"""

import logging

logger = logging.getLogger(__name__)
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional

from database.connection import get_db
from services.jwt_service import jwt_service
from services.auth_service import auth_service
from schemas.auth import UserResponse

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserResponse:
    """Get current authenticated user from HTTP-only cookie"""
    
    # Get token from HTTP-only cookie
    token = request.cookies.get('access_token')
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required"
        )
    
    # Verify JWT token
    payload = jwt_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get user from database
    user_id = int(payload["sub"])
    logger.info(f"Fetching user with ID: {user_id}")
    user = auth_service.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    
    return UserResponse(
        user_id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        user_type=user.user_type,
        is_active=user.is_active,
        is_verified=user.is_verified
    )

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[UserResponse]:
    """Get current authenticated user, but don't raise error if not authenticated"""
    
    try:
        return get_current_user(request, db)
    except HTTPException:
        return None