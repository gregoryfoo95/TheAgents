from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import urllib.parse
import logging

logger = logging.getLogger(__name__)

from database.connection import get_db
from services.oauth_service import oauth_service
from services.oauth_service import oauth_service
from services.auth_service import auth_service
from schemas.auth import (
    OAuthProvidersResponse, LoginResponse, RefreshTokenRequest,
    UserTypeSelectionData, AuthCallbackResponse, SuccessResponse
)
from middleware.auth import get_current_user
from schemas.auth import UserResponse

oauth_router = APIRouter(tags=["auth"])


@oauth_router.get(
    "/providers",
    response_model=OAuthProvidersResponse,
    summary="Get available OAuth providers",
    description="Get list of available OAuth authentication providers"
)
async def get_oauth_providers():
    """Get available OAuth providers."""
    providers = oauth_service.get_available_providers()
    return OAuthProvidersResponse(providers=providers)


@oauth_router.get(
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
    auth_url = oauth_service.get_authorization_url(
        provider_name="google",
        state=state
    )

    # Redirect to Google OAuth
    return RedirectResponse(url=auth_url)


@oauth_router.get(
    "/callback/google",
    response_model=AuthCallbackResponse,
    summary="Handle Google OAuth callback",
    description="Handle OAuth callback and create JWT tokens"
)
async def google_oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: Optional[str] = Query(None, description="OAuth state parameter"),
    error: Optional[str] = Query(None, description="OAuth error"),
    db: Session = Depends(get_db)
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
            logger.info(f"Frontend redirect URI: {frontend_redirect_uri}")
            
        # Exchange authorization code for tokens
        oauth_tokens = await oauth_service.exchange_code_for_tokens(
            provider_name="google",
            code=code
        )

        # Get user info from Google
        user_info = await oauth_service.get_user_info(
            provider_name="google",
            access_token=oauth_tokens.access_token
        )

        # Create or get user using auth service
        user = await auth_service.authenticate_or_create_oauth_user(
            db=db,
            provider="google",
            oauth_user_info=user_info,
            oauth_tokens=oauth_tokens
        )

        # Create user session with JWT tokens
        session_data = await auth_service.create_user_session(user)
        jwt_tokens = {
            'access_token': session_data['access_token'],
            'refresh_token': session_data['refresh_token'],
            'token_type': session_data['token_type']
        }
        
        logger.info(f"✅ OAuth Session created for user {user.email}")
        logger.info(f"🔑 Access token: {jwt_tokens['access_token'][:50]}...")
        logger.info(f"🔄 Refresh token: {jwt_tokens['refresh_token'][:50]}...")

        # Determine redirect URL - use provided frontend_redirect_uri or default
        redirect_url = frontend_redirect_uri or "http://localhost:3000/dashboard"
        
        # Always create redirect response with HTTP-only cookies
        response = RedirectResponse(url=redirect_url)
        
        # Set secure HTTP-only cookies for tokens
        logger.info(f"🍪 Setting access_token cookie: {jwt_tokens['access_token'][:50]}...")
        response.set_cookie(
            key="access_token",
            value=jwt_tokens['access_token'],
            max_age=24 * 60 * 60,  # 24 hours
            httponly=True,  # Prevent XSS
            secure=False,   # Set to True in production with HTTPS
            samesite="lax",  # CSRF protection
            path="/",       # Explicitly set path
            domain=None     # Let browser determine domain
        )
        
        if jwt_tokens.get('refresh_token'):
            logger.info(f"🍪 Setting refresh_token cookie: {jwt_tokens['refresh_token'][:50]}...")
            response.set_cookie(
                key="refresh_token", 
                value=jwt_tokens['refresh_token'],
                max_age=30 * 24 * 60 * 60,  # 30 days
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax",
                path="/",       # Explicitly set path
                domain=None     # Let browser determine domain
            )
        else:
            logger.warning("⚠️  No refresh token to set as cookie")
        
        # Add user info to URL for frontend session storage
        user_params = urllib.parse.urlencode({
            'auth': 'success',
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user.user_type.value if user.user_type else '',
            'needs_role_selection': 'true' if user.user_type is None else 'false',
            'profile_picture_url': user.profile_picture_url or ''
        })
        redirect_url_with_user_info = f"{redirect_url}?{user_params}"
        response.headers["location"] = redirect_url_with_user_info
        
        logger.info(f"🔀 Redirecting to: {redirect_url_with_user_info}")
        logger.info(f"📤 Response cookies being set: access_token, refresh_token")
        
        return response

    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@oauth_router.put(
    "/user-type",
    response_model=UserResponse,
    summary="Update user type",
    description="Update user type (consumer/agent/lawyer) for authenticated user"
)
async def update_user_type(
    user_data: UserTypeSelectionData,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
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
        # Update user type using authenticated user's ID
        updated_user = auth_service.update_user_type(
            db=db,
            user_id=current_user.id,
            user_type=user_data.user_type,
            phone=user_data.phone
        )
        
        logger.info(f"User type update successful for user ID {current_user.id}")
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            display_name=updated_user.display_name,
            profile_picture_url=updated_user.profile_picture_url,
            user_type=updated_user.user_type,
            is_active=updated_user.is_active,
            is_verified=updated_user.is_verified,
            email_verified=updated_user.email_verified,
            created_at=updated_user.created_at,
            last_login=updated_user.last_login
        )

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


@oauth_router.post(
    "/logout",
    response_model=SuccessResponse,
    summary="Logout user",
    description="Logout current authenticated user and clear session"
)
async def logout_user(
    response: Response,
    current_user: UserResponse = Depends(get_current_user)
):
    """Logout user and clear session."""
    try:
        success = await auth_service.logout_user(current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
        
        # Clear HTTP-only cookies
        response.delete_cookie(
            key="access_token",
            path="/",
            httponly=True
        )
        response.delete_cookie(
            key="refresh_token", 
            path="/",
            httponly=True
        )
        
        return SuccessResponse(message="Successfully logged out")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@oauth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get current authenticated user information"
)
async def get_current_user_profile(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    client_host = request.client.host if request.client else "unknown"
    logger.info(f"🔐 Auth Service: Direct request to /auth/me from {client_host}")
    try:
        # Get full user data from database
        user = auth_service.get_user_by_id(db, current_user.id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            profile_picture_url=user.profile_picture_url,
            user_type=user.user_type,
            is_active=user.is_active,
            is_verified=user.is_verified,
            email_verified=user.email_verified,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@oauth_router.get(
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