import redis.asyncio as redis
import json
from typing import Optional, Any, Union
from functools import wraps
import pickle
import logging

from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisClient:
    """Async Redis client with error handling and serialization support."""

    def __init__(self):
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            retry_on_timeout=True,
            retry_on_error=[redis.ConnectionError, redis.TimeoutError]
        )

    async def get(self, key: str) -> Optional[str]:
        """Get string value from Redis."""
        try:
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set string value in Redis with optional expiration."""
        try:
            return await self.redis.set(key, value, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from Redis."""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Redis GET JSON error for key {key}: {e}")
            return None

    async def set_json(
        self,
        key: str,
        value: Union[dict, list],
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value in Redis."""
        try:
            json_str = json.dumps(value, default=str)
            return await self.redis.set(key, json_str, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET JSON error for key {key}: {e}")
            return False

    async def get_object(self, key: str) -> Optional[Any]:
        """Get pickled object from Redis."""
        try:
            value = await self.redis.get(key)
            return pickle.loads(value.encode()) if value else None
        except Exception as e:
            logger.error(f"Redis GET object error for key {key}: {e}")
            return None

    async def set_object(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set pickled object in Redis."""
        try:
            pickled_value = pickle.dumps(value).decode('latin-1')
            return await self.redis.set(key, pickled_value, ex=expire)
        except Exception as e:
            logger.error(f"Redis SET object error for key {key}: {e}")
            return False

    async def delete(self, *keys: str) -> int:
        """Delete keys from Redis."""
        try:
            return await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a key by amount."""
        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key."""
        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        try:
            return await self.redis.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []

    async def flush_db(self) -> bool:
        """Flush current database (use with caution!)."""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False

    async def ping(self) -> bool:
        """Ping Redis to check connection."""
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis PING error: {e}")
            return False

    async def close(self):
        """Close Redis connection."""
        try:
            await self.redis.close()
        except Exception as e:
            logger.error(f"Redis CLOSE error: {e}")


# Global Redis client instance
redis_client = RedisClient()


def cache_result(
    expire: int = 3600,
    key_prefix: str = "",
    serialize_method: str = "json"  # "json" or "pickle"
):
    """
    Decorator to cache function results in Redis.

    Args:
        expire: Expiration time in seconds
        key_prefix: Prefix for cache key
        serialize_method: "json" or "pickle" for serialization
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            if serialize_method == "json":
                cached_result = await redis_client.get_json(cache_key)
            else:
                cached_result = await redis_client.get_object(cache_key)

            if cached_result is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)

            if serialize_method == "json":
                await redis_client.set_json(cache_key, result, expire)
            else:
                await redis_client.set_object(cache_key, result, expire)

            logger.debug(f"Cache miss for key: {cache_key}")
            return result
        return wrapper
    return decorator


async def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate all cache keys matching a pattern."""
    keys = await redis_client.keys(pattern)
    if keys:
        return await redis_client.delete(*keys)
    return 0
