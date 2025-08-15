import redis
from config import settings
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
    async def set_user_session(self, user_id: int, session_data: dict, expire_hours: int = 24):
        """Store user session data in Redis"""
        try:
            key = f"user_session:{user_id}"
            serialized_data = json.dumps(session_data)
            expire_seconds = expire_hours * 3600
            
            self.redis_client.setex(key, expire_seconds, serialized_data)
            logger.info(f"User session stored for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to store user session: {e}")
            return False
    
    async def get_user_session(self, user_id: int) -> Optional[dict]:
        """Get user session data from Redis"""
        try:
            key = f"user_session:{user_id}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get user session: {e}")
            return None
    
    async def delete_user_session(self, user_id: int) -> bool:
        """Delete user session from Redis"""
        try:
            key = f"user_session:{user_id}"
            result = self.redis_client.delete(key)
            logger.info(f"User session deleted for user {user_id}")
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete user session: {e}")
            return False
    
    async def cache_user_data(self, user_id: int, user_data: dict, expire_minutes: int = 15):
        """Cache user data for quick validation across services"""
        try:
            key = f"user_cache:{user_id}"
            serialized_data = json.dumps(user_data)
            expire_seconds = expire_minutes * 60
            
            self.redis_client.setex(key, expire_seconds, serialized_data)
            return True
        except Exception as e:
            logger.error(f"Failed to cache user data: {e}")
            return False
    
    async def get_cached_user_data(self, user_id: int) -> Optional[dict]:
        """Get cached user data"""
        try:
            key = f"user_cache:{user_id}"
            data = self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get cached user data: {e}")
            return None

# Global Redis client instance
redis_client = RedisClient()