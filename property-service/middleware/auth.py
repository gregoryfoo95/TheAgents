from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import logging
from typing import Optional
from config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

class AuthService:
    def __init__(self):
        self.auth_service_url = settings.auth_service_url
    
    async def validate_token(self, token: str) -> dict:
        """Validate token with auth service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.auth_service_url}/auth/validate",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token validation failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Auth service communication error: {e}")
            return None

auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user_data = await auth_service.validate_token(credentials.credentials)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    return user_data

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """Optional dependency to get current user (for public endpoints)"""
    if not credentials:
        return None
    
    try:
        user_data = await auth_service.validate_token(credentials.credentials)
        return user_data
    except:
        return None

def require_user_type(allowed_types: list):
    """Decorator factory to require specific user types"""
    def decorator(user: dict = Depends(get_current_user)):
        if user["user_type"] not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return decorator

# Common permission decorators
require_homeowner = require_user_type(["homeowner"])
require_tenant = require_user_type(["tenant"])
require_lawyer = require_user_type(["lawyer"])
require_homeowner_or_lawyer = require_user_type(["homeowner", "lawyer"])