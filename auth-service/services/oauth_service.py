"""Scalable OAuth 2.0 service with provider registry pattern."""

from typing import Dict, Optional
from fastapi import HTTPException, status
import logging

from config import settings
from models.user import AuthProvider
from .oauth_providers import (
    OAuthProvider, 
    GoogleOAuthProvider, 
    GitHubOAuthProvider,
    MicrosoftOAuthProvider,
    LinkedInOAuthProvider
)

logger = logging.getLogger(__name__)

class OAuthService:
    """Scalable OAuth service supporting multiple providers via provider registry pattern."""
    
    def __init__(self):
        self.settings = settings
        self.providers: Dict[str, OAuthProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize OAuth providers based on configuration."""
        # Register Google provider
        if self.settings.google_client_id and self.settings.google_client_secret:
            self.providers['google'] = GoogleOAuthProvider(
                client_id=self.settings.google_client_id,
                client_secret=self.settings.google_client_secret,
                redirect_uri=self.settings.oauth_redirect_uri
            )
            logger.info("Registered Google OAuth provider")
        
        # Register GitHub provider (if configured)
        if hasattr(self.settings, 'github_client_id') and self.settings.github_client_id:
            self.providers['github'] = GitHubOAuthProvider(
                client_id=self.settings.github_client_id,
                client_secret=self.settings.github_client_secret,
                redirect_uri=self.settings.oauth_redirect_uri.replace('google', 'github')
            )
            logger.info("Registered GitHub OAuth provider")
        
        # Register Microsoft provider (if configured)
        if hasattr(self.settings, 'microsoft_client_id') and self.settings.microsoft_client_id:
            self.providers['microsoft'] = MicrosoftOAuthProvider(
                client_id=self.settings.microsoft_client_id,
                client_secret=self.settings.microsoft_client_secret,
                redirect_uri=self.settings.oauth_redirect_uri.replace('google', 'microsoft')
            )
            logger.info("Registered Microsoft OAuth provider")
        
        # Register LinkedIn provider (if configured)
        if hasattr(self.settings, 'linkedin_client_id') and self.settings.linkedin_client_id:
            self.providers['linkedin'] = LinkedInOAuthProvider(
                client_id=self.settings.linkedin_client_id,
                client_secret=self.settings.linkedin_client_secret,
                redirect_uri=self.settings.oauth_redirect_uri.replace('google', 'linkedin')
            )
            logger.info("Registered LinkedIn OAuth provider")
    
    def get_available_providers(self) -> list[str]:
        """Get list of available OAuth providers."""
        return list(self.providers.keys())
    
    def get_provider(self, provider_name: str) -> OAuthProvider:
        """Get OAuth provider instance."""
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OAuth provider '{provider_name}' not supported or configured"
            )
        return provider
    
    def get_authorization_url(self, provider_name: str, state: Optional[str] = None, 
                            scopes: Optional[list[str]] = None) -> str:
        """Generate OAuth authorization URL for the specified provider."""
        provider = self.get_provider(provider_name)
        return provider.get_authorization_url(state=state, scopes=scopes)
    
    async def exchange_code_for_tokens(self, provider_name: str, code: str):
        """Exchange authorization code for access tokens."""
        provider = self.get_provider(provider_name)
        return await provider.exchange_code_for_tokens(code)
    
    async def get_user_info(self, provider_name: str, access_token: str):
        """Get user information from OAuth provider."""
        provider = self.get_provider(provider_name)
        return await provider.get_user_info(access_token)
    
    async def refresh_access_token(self, provider_name: str, refresh_token: str):
        """Refresh access token (if supported by provider)."""
        provider = self.get_provider(provider_name)
        return await provider.refresh_access_token(refresh_token)
    
    async def revoke_token(self, provider_name: str, token: str) -> bool:
        """Revoke access token."""
        try:
            provider = self.get_provider(provider_name)
            return await provider.revoke_token(token)
        except Exception as e:
            logger.warning(f"Failed to revoke token for {provider_name}: {e}")
            return False
    
    def is_provider_available(self, provider_name: str) -> bool:
        """Check if OAuth provider is available and configured."""
        return provider_name in self.providers
    
    def register_provider(self, provider: OAuthProvider) -> None:
        """Dynamically register a new OAuth provider."""
        self.providers[provider.provider_name] = provider
        logger.info(f"Registered OAuth provider: {provider.provider_name}")


# Singleton instance
oauth_service = OAuthService()