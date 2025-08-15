"""GitHub OAuth provider implementation"""

import httpx
from typing import Dict, Any
from datetime import datetime, timezone
from .base import OAuthProvider, OAuthUserInfo, OAuthTokens
from fastapi import HTTPException, status

class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth provider"""
    
    @property
    def provider_name(self) -> str:
        return "github"
    
    @property
    def authorize_url(self) -> str:
        return "https://github.com/login/oauth/authorize"
    
    @property
    def token_url(self) -> str:
        return "https://github.com/login/oauth/access_token"
    
    @property
    def user_info_url(self) -> str:
        return "https://api.github.com/user"
    
    @property
    def default_scopes(self) -> list[str]:
        return ["user:email"]  # Need email scope to get email addresses
    
    async def exchange_code_for_tokens(self, code: str) -> OAuthTokens:
        """Exchange authorization code for GitHub tokens"""
        token_data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
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
                
                return OAuthTokens(
                    access_token=token_response['access_token'],
                    token_type=token_response.get('token_type', 'Bearer'),
                    scope=token_response.get('scope')
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for GitHub tokens: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from GitHub"""
        try:
            async with httpx.AsyncClient() as client:
                # Get user profile
                user_response = await client.get(
                    self.user_info_url,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_response.raise_for_status()
                user_data = user_response.json()
                
                # Get user emails (GitHub doesn't include email in user profile by default)
                email = user_data.get('email')
                email_verified = False
                
                if not email:
                    email_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers={'Authorization': f'Bearer {access_token}'}
                    )
                    if email_response.status_code == 200:
                        emails = email_response.json()
                        # Find primary email
                        for email_info in emails:
                            if email_info.get('primary', False):
                                email = email_info['email']
                                email_verified = email_info.get('verified', False)
                                break
                        # Fallback to first email if no primary
                        if not email and emails:
                            email = emails[0]['email']
                            email_verified = emails[0].get('verified', False)
                
                # Parse name
                name = user_data.get('name', '').strip()
                first_name, last_name = '', ''
                if name:
                    name_parts = name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                return OAuthUserInfo(
                    provider_user_id=str(user_data['id']),
                    email=email or '',
                    first_name=first_name,
                    last_name=last_name,
                    display_name=name or user_data.get('login'),
                    username=user_data.get('login'),
                    profile_picture_url=user_data.get('avatar_url'),
                    email_verified=email_verified,
                    raw_data=user_data
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from GitHub: {str(e)}"
            )