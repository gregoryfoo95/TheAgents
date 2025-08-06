"""OAuth 2.0 service for handling authentication with various providers."""

import httpx
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import HTTPException, status

from utilities.config import get_settings

# Constants for OAuth 2.0 endpoints
AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

class OAuthProvider:
    """Base OAuth provider configuration."""

    def __init__(self, name: str, client_id: str, client_secret: str,
                 authorize_url: str, token_url: str, user_info_url: str):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.user_info_url = user_info_url


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth 2.0 provider."""

    def __init__(self, client_id: str, client_secret: str):
        super().__init__(
            name="google",
            client_id=client_id,
            client_secret=client_secret,
            authorize_url=AUTHORIZE_URL,
            token_url=TOKEN_URL,
            user_info_url=USER_INFO_URL
        )


class OAuthService:
    """Generic OAuth 2.0 service for handling multiple providers."""

    def __init__(self):
        self.settings = get_settings()
        self.providers = self._initialize_providers()

    def _initialize_providers(self) -> Dict[str, OAuthProvider]:
        """Initialize OAuth providers based on configuration."""
        providers = {}

        # Google OAuth
        if hasattr(self.settings, 'google_client_id') and self.settings.google_client_id:
            providers['google'] = GoogleOAuthProvider(
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret
            )

        return providers

    def get_available_providers(self) -> list[str]:
        """Get list of available OAuth providers."""
        return list(self.providers.keys())

    def get_authorization_url(self, provider_name: str, redirect_uri: str,
                            state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL for the specified provider."""
        if provider_name not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider_name}' not supported"
            )

        provider = self.providers[provider_name]

        # OAuth 2.0 authorization parameters
        params = {
            'client_id': provider.client_id,
            'response_type': 'code',
            'scope': self._get_provider_scopes(provider_name),
            'redirect_uri': redirect_uri,
            'access_type': 'offline',  # For refresh token (Google)
            'prompt': 'consent'  # Force consent screen (Google)
        }

        if state:
            params['state'] = state

        return f"{provider.authorize_url}?{urlencode(params)}"

    def _get_provider_scopes(self, provider_name: str) -> str:
        """Get OAuth scopes for the provider."""
        scopes = {
            'google': 'openid email profile',
        }
        return scopes.get(provider_name, 'email profile')

    async def exchange_code_for_tokens(self, provider_name: str, code: str,
                                     redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        if provider_name not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider_name}' not supported"
            )

        provider = self.providers[provider_name]

        # Create OAuth client
        client = AsyncOAuth2Client(
            client_id=provider.client_id,
            client_secret=provider.client_secret
        )

        try:
            # Exchange code for tokens
            token_response = await client.fetch_token(
                url=provider.token_url,
                code=code,
                redirect_uri=redirect_uri
            )

            return token_response

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for tokens: {str(e)}"
            )

    async def get_user_info(self, provider_name: str, access_token: str) -> Dict[str, Any]:
        """Get user information from OAuth provider."""
        if provider_name not in self.providers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider_name}' not supported"
            )

        provider = self.providers[provider_name]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    provider.user_info_url,
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                response.raise_for_status()

                user_info = response.json()

                # Normalize user info across providers
                return self._normalize_user_info(provider_name, user_info)

        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from {provider_name}: {str(e)}"
            )

    def _normalize_user_info(self, provider_name: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user info format across different OAuth providers."""
        if provider_name == 'google':
            return {
                'id': user_info.get('id'),
                'email': user_info.get('email'),
                'first_name': user_info.get('given_name', ''),
                'last_name': user_info.get('family_name', ''),
                'full_name': user_info.get('name', ''),
                'profile_picture_url': user_info.get('picture'),
                'email_verified': user_info.get('verified_email', False)
            }

        # Add other providers here as needed
        return user_info

    async def validate_token(self, provider_name: str, access_token: str) -> bool:
        """Validate if the access token is still valid."""
        try:
            await self.get_user_info(provider_name, access_token)
            return True
        except HTTPException:
            return False


# Singleton instance
oauth_service = OAuthService()
