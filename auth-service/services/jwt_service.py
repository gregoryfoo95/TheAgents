import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from config import settings
import logging

logger = logging.getLogger(__name__)

class JWTService:
    def __init__(self):
        self.secret_key = settings.jwt_secret
        self.algorithm = settings.jwt_algorithm
        self.expiration_hours = settings.jwt_expiration_hours
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        try:
            # Prepare token payload
            expire_time = datetime.now(timezone.utc) + timedelta(hours=self.expiration_hours)
            
            payload = {
                "sub": str(user_data["id"]),  # Subject (user ID)
                "email": user_data["email"],
                "user_type": user_data["user_type"],
                "exp": expire_time,  # Expiration time
                "iat": datetime.now(timezone.utc),  # Issued at
                "type": "access_token"
            }
            
            # Create and return token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"JWT token created for user {user_data['id']}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise ValueError("Failed to create access token")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            # Decode and verify token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != "access_token":
                logger.warning("Invalid token type")
                return None
            
            # Check expiration
            if datetime.now(timezone.utc) > datetime.fromtimestamp(payload["exp"], tz=timezone.utc):
                logger.warning("Token has expired")
                return None
            
            logger.debug(f"Token verified for user {payload['sub']}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create JWT refresh token"""
        try:
            expire_time = datetime.now(timezone.utc) + timedelta(days=30)  # Refresh tokens last longer
            
            payload = {
                "sub": str(user_id),
                "exp": expire_time,
                "iat": datetime.now(timezone.utc),
                "type": "refresh_token"
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Refresh token created for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise ValueError("Failed to create refresh token")
    
    def get_user_id_from_token(self, token: str) -> Optional[int]:
        """Extract user ID from token without full verification"""
        try:
            # Decode without verification to get user ID
            payload = jwt.decode(token, options={"verify_signature": False})
            return int(payload.get("sub"))
        except:
            return None

# Global JWT service instance
jwt_service = JWTService()