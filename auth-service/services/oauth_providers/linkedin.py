"""LinkedIn OAuth provider implementation"""

import httpx
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from .base import OAuthProvider, OAuthUserInfo, OAuthTokens
from fastapi import HTTPException, status

class LinkedInOAuthProvider(OAuthProvider):
    """LinkedIn OAuth provider"""
    
    @property
    def provider_name(self) -> str:
        return "linkedin"
    
    @property
    def authorize_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/authorization"
    
    @property
    def token_url(self) -> str:
        return "https://www.linkedin.com/oauth/v2/accessToken"
    
    @property
    def user_info_url(self) -> str:
        return "https://api.linkedin.com/v2/people/~"
    
    @property
    def default_scopes(self) -> list[str]:
        return ["r_liteprofile", "r_emailaddress"]
    
    async def exchange_code_for_tokens(self, code: str) -> OAuthTokens:
        """Exchange authorization code for LinkedIn tokens"""
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
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
                    expires_at=expires_at,
                    token_type=token_response.get('token_type', 'Bearer'),
                    scope=token_response.get('scope')
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for LinkedIn tokens: {str(e)}"
            )
    
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information from LinkedIn"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {'Authorization': f'Bearer {access_token}'}
                
                # Get profile information
                profile_response = await client.get(
                    "https://api.linkedin.com/v2/people/~:(id,firstName,lastName,profilePicture(displayImage~:playableStreams))",
                    headers=headers
                )
                profile_response.raise_for_status()
                profile_data = profile_response.json()
                
                # Get email address
                email_response = await client.get(
                    "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
                    headers=headers
                )
                email_response.raise_for_status()
                email_data = email_response.json()
                
                # Extract email
                email = ''
                if email_data.get('elements'):
                    email = email_data['elements'][0].get('handle~', {}).get('emailAddress', '')
                
                # Extract profile picture
                profile_picture_url = None
                if profile_data.get('profilePicture'):
                    display_image = profile_data['profilePicture'].get('displayImage~')
                    if display_image and display_image.get('elements'):
                        # Get largest image
                        profile_picture_url = display_image['elements'][-1].get('identifiers', [{}])[0].get('identifier')
                
                # Extract names
                first_name = profile_data.get('firstName', {}).get('localized', {}).get('en_US', '')
                last_name = profile_data.get('lastName', {}).get('localized', {}).get('en_US', '')
                display_name = f"{first_name} {last_name}".strip()
                
                return OAuthUserInfo(
                    provider_user_id=str(profile_data['id']),
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    display_name=display_name,
                    profile_picture_url=profile_picture_url,
                    email_verified=True,  # LinkedIn emails are generally verified
                    raw_data={**profile_data, 'email_data': email_data}
                )
                
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from LinkedIn: {str(e)}"
            )