"""OAuth provider implementations"""

from .base import OAuthProvider, OAuthUserInfo
from .google import GoogleOAuthProvider
from .github import GitHubOAuthProvider
from .microsoft import MicrosoftOAuthProvider
from .linkedin import LinkedInOAuthProvider

__all__ = [
    'OAuthProvider',
    'OAuthUserInfo', 
    'GoogleOAuthProvider',
    'GitHubOAuthProvider',
    'MicrosoftOAuthProvider',
    'LinkedInOAuthProvider'
]