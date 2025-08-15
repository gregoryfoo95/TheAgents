"""Google OAuth provider implementation"""

import httpx
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from .base import OAuthProvider, OAuthUserInfo, OAuthTokens
from fastapi import HTTPException, status

class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider"""
    
    @property
    def provider_name(self) -> str:
        return "google"
    
    @property
    def authorize_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"
    
    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"
    
    @property
    def user_info_url(self) -> str:
        return "https://www.googleapis.com/oauth2/v2/userinfo"
    
    @property
    def default_scopes(self) -> list[str]:
        return ["openid", "email", "profile"]
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        return {
            'access_type': 'offline',  # Request refresh token
            'prompt': 'consent'  # Force consent screen for refresh token
        }
    
    async def exchange_code_for_tokens(self, code: str) -> OAuthTokens:
        """Exchange authorization code for Google tokens"""
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=token_data,
                    headers={'Accept': 'application/json'}
                )
                response.raise_for_status()
                
                token_response = response.json()
                
                expires_at = None
                if 'expires_in' in token_response:
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response['expires_in'])
                
                return OAuthTokens(
                    access_token=token_response['access_token'],
                    refresh_token=token_response.get('refresh_token'),
                    expires_at=expires_at,
                    token_type=token_response.get('token_type', 'Bearer'),
                    scope=token_response.get('scope')
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for tokens: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from Google"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.user_info_url,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()
                
                user_data = response.json()
                
                return OAuthUserInfo(
                    provider_user_id=str(user_data['id']),
                    email=user_data['email'],
                    first_name=user_data.get('given_name', ''),
                    last_name=user_data.get('family_name', ''),
                    display_name=user_data.get('name'),
                    profile_picture_url=user_data.get('picture'),
                    email_verified=user_data.get('verified_email', False),
                    raw_data=user_data
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from Google: {str(e)}"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokens:
        """Refresh Google access token"""
        refresh_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.token_url,
                    data=refresh_data,
                    headers={'Accept': 'application/json'}
                )
                response.raise_for_status()
                
                token_response = response.json()
                
                expires_at = None
                if 'expires_in' in token_response:
                    expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_response['expires_in'])
                
                return OAuthTokens(
                    access_token=token_response['access_token'],
                    refresh_token=refresh_token,  # Google may or may not return new refresh token
                    expires_at=expires_at,
                    token_type=token_response.get('token_type', 'Bearer'),
                    scope=token_response.get('scope')
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to refresh Google token: {str(e)}"
            )
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke Google access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://oauth2.googleapis.com/revoke?token={token}"
                )
                return response.status_code == 200
        except:
            return False