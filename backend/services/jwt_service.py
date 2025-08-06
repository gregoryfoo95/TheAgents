"""JWT token service for handling access and refresh tokens."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status

from utilities.config import get_settings


class JWTService:
    """Service for handling JWT token creation, validation, and management."""

    def __init__(self):
        self.settings = get_settings()
        self.redis_client = redis.Redis.from_url(self.settings.redis_url, decode_responses=True)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.settings.jwt_access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm
        )
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.settings.jwt_refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm
        )
        return encoded_jwt

    def create_token_pair(self, user_id: int, email: str, user_type: str) -> Dict[str, Any]:
        """Create both access and refresh tokens for a user."""
        token_data = {
            "sub": str(user_id),
            "email": email,
            "user_type": user_type
        }

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        # Store refresh token in Redis for session management
        self._store_refresh_token(user_id, refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.settings.jwt_access_token_expire_minutes * 60,
            "refresh_expires_in": self.settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        }

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )

            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Create a new access token using a valid refresh token."""
        # Verify refresh token
        payload = self.verify_token(refresh_token, token_type="refresh")

        user_id = int(payload.get("sub"))
        email = payload.get("email")
        user_type = payload.get("user_type")

        # Check if refresh token is still valid in Redis
        if not self._is_refresh_token_valid(user_id, refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new access token
        token_data = {
            "sub": str(user_id),
            "email": email,
            "user_type": user_type
        }

        new_access_token = self.create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.settings.jwt_access_token_expire_minutes * 60
        }

    def revoke_user_tokens(self, user_id: int) -> bool:
        """Revoke all refresh tokens for a user (logout from all devices)."""
        try:
            # Remove all refresh tokens for the user
            pattern = f"refresh_token:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception:
            return False

    def revoke_refresh_token(self, user_id: int, refresh_token: str) -> bool:
        """Revoke a specific refresh token (logout from specific device)."""
        try:
            # Create a hash of the token for storage
            token_hash = self._hash_token(refresh_token)
            key = f"refresh_token:{user_id}:{token_hash}"

            # Remove the specific refresh token
            result = self.redis_client.delete(key)
            return result > 0
        except Exception:
            return False

    def _store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """Store refresh token in Redis with expiration."""
        token_hash = self._hash_token(refresh_token)
        key = f"refresh_token:{user_id}:{token_hash}"

        # Store with expiration time
        expiration_seconds = self.settings.jwt_refresh_token_expire_days * 24 * 60 * 60
        self.redis_client.setex(key, expiration_seconds, "valid")

    def _is_refresh_token_valid(self, user_id: int, refresh_token: str) -> bool:
        """Check if refresh token exists and is valid in Redis."""
        try:
            token_hash = self._hash_token(refresh_token)
            key = f"refresh_token:{user_id}:{token_hash}"
            return self.redis_client.exists(key) > 0
        except Exception:
            return False

    def _hash_token(self, token: str) -> str:
        """Create a hash of the token for storage."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    def get_user_active_sessions(self, user_id: int) -> int:
        """Get the number of active sessions (refresh tokens) for a user."""
        try:
            pattern = f"refresh_token:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            return len(keys)
        except Exception:
            return 0

    def blacklist_token(self, token: str) -> bool:
        """Add an access token to blacklist (for immediate logout)."""
        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
                options={"verify_exp": False}  # Don't verify expiration for blacklisting
            )

            exp = payload.get("exp")
            if exp:
                # Calculate remaining time until expiration
                exp_datetime = datetime.utcfromtimestamp(exp)
                remaining_time = (exp_datetime - datetime.utcnow()).total_seconds()

                if remaining_time > 0:
                    # Add to blacklist with expiration
                    token_hash = self._hash_token(token)
                    key = f"blacklist:{token_hash}"
                    self.redis_client.setex(key, int(remaining_time), "blacklisted")
                    return True

            return False
        except Exception:
            return False

    def is_token_blacklisted(self, token: str) -> bool:
        """Check if an access token is blacklisted."""
        try:
            token_hash = self._hash_token(token)
            key = f"blacklist:{token_hash}"
            return self.redis_client.exists(key) > 0
        except Exception:
            return False


# Singleton instance
jwt_service = JWTService()
