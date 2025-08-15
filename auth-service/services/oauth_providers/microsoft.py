"""Microsoft OAuth provider implementation"""

import httpx
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from .base import OAuthProvider, OAuthUserInfo, OAuthTokens
from fastapi import HTTPException, status

class MicrosoftOAuthProvider(OAuthProvider):
    """Microsoft OAuth provider (Azure AD / Microsoft Graph)"""
    
    @property
    def provider_name(self) -> str:
        return "microsoft"
    
    @property
    def authorize_url(self) -> str:
        return "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    
    @property
    def token_url(self) -> str:
        return "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    
    @property
    def user_info_url(self) -> str:
        return "https://graph.microsoft.com/v1.0/me"
    
    @property
    def default_scopes(self) -> list[str]:
        return ["openid", "profile", "email", "User.Read"]
    
    async def exchange_code_for_tokens(self, code: str) -> OAuthTokens:
        """Exchange authorization code for Microsoft tokens"""
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.default_scopes)
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
                detail=f"Failed to exchange code for Microsoft tokens: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from Microsoft Graph"""
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
                    email=user_data.get('mail') or user_data.get('userPrincipalName', ''),
                    first_name=user_data.get('givenName', ''),
                    last_name=user_data.get('surname', ''),
                    display_name=user_data.get('displayName'),
                    username=user_data.get('userPrincipalName'),
                    profile_picture_url=None,  # Would need separate Graph API call
                    email_verified=True,  # Microsoft accounts are generally verified
                    raw_data=user_data
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from Microsoft: {str(e)}"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokens:
        """Refresh Microsoft access token"""
        refresh_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': ' '.join(self.default_scopes)
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
                    refresh_token=token_response.get('refresh_token', refresh_token),
                    expires_at=expires_at,
                    token_type=token_response.get('token_type', 'Bearer'),
                    scope=token_response.get('scope')
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to refresh Microsoft token: {str(e)}"
            )