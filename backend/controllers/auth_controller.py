"""Authentication controller for OAuth 2.0 and JWT token management."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import secrets
import urllib.parse
import logging

logger = logging.getLogger(__name__)

from utilities.database import get_async_db
from services.oauth_service import oauth_service
from services.jwt_service import jwt_service
from services.user_service import UserService
from schemas.auth import (
    OAuthProvidersResponse, TokenResponse, RefreshTokenRequest,
    UserTypeSelectionData, AuthCallbackResponse
)
from schemas.base import SuccessResponse
from middleware.auth import get_current_user
from schemas.user import User as UserSchema


auth_router = APIRouter(prefix="/api/auth", tags=["authentication"])


@auth_router.get(
    "/providers",
    response_model=OAuthProvidersResponse,
    summary="Get available OAuth providers",
    description="Get list of available OAuth authentication providers"
)
async def get_oauth_providers():
    """Get available OAuth providers."""
    providers = oauth_service.get_available_providers()
    return OAuthProvidersResponse(providers=providers)


@auth_router.get(
    "/google",
    summary="Initiate Google OAuth",
    description="Redirect to Google OAuth authorization page"
)
async def google_oauth_login(
    redirect_uri: Optional[str] = Query(None, description="Frontend redirect URI after auth")
):
    """Initiate Google OAuth authentication flow."""
    if "google" not in oauth_service.get_available_providers():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth is not configured"
        )

    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store redirect_uri in state if provided (in production, use Redis)
    if redirect_uri:
        # Simple encoding for development - use proper session storage in production
        state = f"{state}|{urllib.parse.quote(redirect_uri)}"

    # Get OAuth authorization URL
    oauth_redirect_uri = oauth_service.settings.oauth_redirect_uri
    auth_url = oauth_service.get_authorization_url(
        provider_name="google",
        redirect_uri=oauth_redirect_uri,
        state=state
    )

    # Redirect to Google OAuth
    return RedirectResponse(url=auth_url)


@auth_router.get(
    "/callback/google",
    response_model=AuthCallbackResponse,
    summary="Handle Google OAuth callback",
    description="Handle OAuth callback and create JWT tokens"
)
async def google_oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: Optional[str] = Query(None, description="OAuth state parameter"),
    error: Optional[str] = Query(None, description="OAuth error"),
    db: AsyncSession = Depends(get_async_db)
):
    """Handle Google OAuth callback and create user session."""

    # Check for OAuth errors
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {error}"
        )

    try:
        # Extract redirect URI from state if present
        frontend_redirect_uri = None
        if state and "|" in state:
            _, encoded_redirect = state.split("|", 1)
            frontend_redirect_uri = urllib.parse.unquote(encoded_redirect)
            print(f"Frontend redirect URI: {frontend_redirect_uri}")
        # Exchange authorization code for tokens
        oauth_tokens = await oauth_service.exchange_code_for_tokens(
            provider_name="google",
            code=code,
            redirect_uri=oauth_service.settings.oauth_redirect_uri
        )

        # Get user info from Google
        user_info = await oauth_service.get_user_info(
            provider_name="google",
            access_token=oauth_tokens["access_token"]
        )

        # Create or get user
        user_service = UserService(db)
        user = await user_service.get_or_create_oauth_user(
            oauth_provider="google",
            oauth_id=user_info["id"],
            email=user_info["email"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            profile_picture_url=user_info["profile_picture_url"]
        )

        # Create JWT tokens (user_type can be null for first-time users)
        jwt_tokens = jwt_service.create_token_pair(
            user_id=user.id,
            email=user.email,
            user_type=user.user_type or "pending"  # Use "pending" if user_type is null
        )

        # If frontend redirect URI is provided, redirect there with secure cookies
        if frontend_redirect_uri:
            response = RedirectResponse(url=frontend_redirect_uri)
            
            # Set secure HTTP-only cookies for tokens
            response.set_cookie(
                key="access_token",
                value=jwt_tokens['access_token'],
                max_age=jwt_tokens.get('expires_in', 900),  # 15 minutes default
                httponly=True,  # Prevent XSS
                secure=False,   # Set to True in production with HTTPS
                samesite="lax"  # CSRF protection
            )
            
            if jwt_tokens.get('refresh_token'):
                response.set_cookie(
                    key="refresh_token", 
                    value=jwt_tokens['refresh_token'],
                    max_age=30 * 24 * 60 * 60,  # 30 days
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite="lax"
                )
            
            # Add user info to URL for frontend session storage
            user_params = urllib.parse.urlencode({
                'auth': 'success',
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user.user_type or '',  # Empty if null for role selection
                'needs_role_selection': 'true' if user.user_type is None else 'false',
                'oauth_id': user.oauth_id or '',
                'profile_picture_url': user.profile_picture_url or ''
            })
            redirect_url_with_user_info = f"{frontend_redirect_uri}?{user_params}"
            response.headers["location"] = redirect_url_with_user_info
            return response

        # Return tokens directly
        return AuthCallbackResponse(
            success=True,
            message="Authentication successful",
            tokens=TokenResponse(**jwt_tokens),
            user={
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.user_type,
                "needs_role_selection": user.user_type is None,
                "profile_picture_url": user.profile_picture_url
            }
        )

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using a valid refresh token"
)
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        new_tokens = jwt_service.refresh_access_token(request.refresh_token)
        return TokenResponse(**new_tokens)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token refresh failed: {str(e)}"
        )



@auth_router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Logout user", 
    description="Clear authentication cookies and logout user"
)
async def logout_user_endpoint(
    current_user: UserSchema = Depends(get_current_user)
):
    """Logout user by clearing authentication cookies."""
    try:
        # Use current_user for logging if needed
        logger.info(f"User {current_user.email} logging out")
        # Create success response
        response_data = SuccessResponse(
            message="Successfully logged out",
            data=None
        )
        
        # Create JSON response and clear cookies
        response = JSONResponse(content=response_data.model_dump())
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@auth_router.put(
    "/user-type",
    response_model=UserSchema,
    summary="Update user type",
    description="Update user type (consumer/agent/lawyer) for authenticated user"
)
async def update_user_type(
    user_data: UserTypeSelectionData,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update user type for authenticated OAuth user."""
    logger.info(f"Update user type endpoint called with data: {user_data}")
    
    try:
        if not current_user:
            logger.error("Authentication failed - no current user")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        logger.info(f"Updating user type for user ID {current_user.id} to {user_data.user_type}")
        user_service = UserService(db)
        # Update user type using authenticated user's ID
        updated_user = await user_service.update_user_type_and_info(
            user_id=current_user.id,
            user_type=user_data.user_type,
            phone=user_data.phone
        )
        
        logger.info(f"User type update successful for user ID {current_user.id}")
        return updated_user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User type update failed: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update user information: {str(e)}"
        )


@auth_router.get(
    "/me",
    response_model=UserSchema,
    summary="Get current user",
    description="Get the currently authenticated user's information"
)
async def get_current_user_info(current_user: UserSchema = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@auth_router.get(
    "/roles",
    summary="Get available user roles",
    description="Get list of available user roles for selection"
)
async def get_user_roles():
    """Get available user roles."""
    return {
        "roles": [
            {
                "value": "consumer",
                "label": "Consumer",
                "description": "Looking to buy or rent properties"
            },
            {
                "value": "agent", 
                "label": "Agent",
                "description": "Real estate professional listing and selling properties"
            },
            {
                "value": "lawyer",
                "label": "Lawyer", 
                "description": "Legal professional providing real estate law services"
            }
        ]
    }


@auth_router.get(
    "/sessions",
    summary="Get active sessions",
    description="Get number of active sessions for current user"
)
async def get_active_sessions(current_user: UserSchema = Depends(get_current_user)):
    """Get active sessions count for current user."""
    session_count = jwt_service.get_user_active_sessions(current_user.id)
    return {"active_sessions": session_count}


@auth_router.post(
    "/revoke-all-sessions",
    response_model=SuccessResponse,
    summary="Revoke all sessions",
    description="Revoke all active sessions (logout from all devices)"
)
async def revoke_all_sessions(current_user: UserSchema = Depends(get_current_user)):
    """Revoke all active sessions for current user."""
    try:
        success = jwt_service.revoke_user_tokens(current_user.id)
        if success:
            return SuccessResponse(message="All sessions revoked successfully", data=None)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to revoke sessions"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke sessions: {str(e)}"
        )
