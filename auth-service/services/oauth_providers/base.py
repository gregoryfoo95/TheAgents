"""Base OAuth provider interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone

@dataclass
class OAuthUserInfo:
    """Normalized user information from OAuth providers"""
    provider_user_id: str
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    username: Optional[str] = None
    profile_picture_url: Optional[str] = None
    email_verified: bool = False
    raw_data: Optional[Dict[str, Any]] = None

@dataclass  
class OAuthTokens:
    """OAuth token information"""
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    token_type: str = "Bearer"
    scope: Optional[str] = None

class OAuthProvider(ABC):
    """Base OAuth provider interface"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier"""
        pass
    
    @property
    @abstractmethod
    def authorize_url(self) -> str:
        """OAuth authorization endpoint"""
        pass
    
    @property
    @abstractmethod
    def token_url(self) -> str:
        """OAuth token exchange endpoint"""
        pass
    
    @property
    @abstractmethod
    def user_info_url(self) -> str:
        """User information endpoint"""
        pass
    
    @property
    @abstractmethod
    def default_scopes(self) -> list[str]:
        """Default OAuth scopes for this provider"""
        pass
    
    def get_authorization_url(self, state: Optional[str] = None, scopes: Optional[list[str]] = None) -> str:
        """Generate OAuth authorization URL"""
        from urllib.parse import urlencode
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes or self.default_scopes),
        }
        
        if state:
            params['state'] = state
            
        # Add provider-specific parameters
        params.update(self.get_additional_auth_params())
        
        return f"{self.authorize_url}?{urlencode(params)}"
    
    @abstractmethod
    async def exchange_code_for_tokens(self, code: str) -> OAuthTokens:
        """Exchange authorization code for access tokens"""
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """Get user information using access token"""
        pass
    
    async def refresh_access_token(self, refresh_token: str) -> OAuthTokens:
        """Refresh access token (optional, not all providers support)"""
        raise NotImplementedError(f"{self.provider_name} does not support token refresh")
    
    def get_additional_auth_params(self) -> Dict[str, str]:
        """Provider-specific authorization parameters"""
        return {}
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke access token (optional)"""
        return True  # Default: assume success