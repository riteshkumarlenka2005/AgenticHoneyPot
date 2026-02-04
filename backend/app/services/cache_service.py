"""Redis caching service with decorators."""
from typing import Any, Callable, Optional
from functools import wraps
import json
import redis.asyncio as redis
from app.config import settings


class CacheService:
    """Redis caching service."""

    def __init__(self):
        """Initialize cache service."""
        self.redis: Optional[redis.Redis] = None
        self.default_ttl = 300  # 5 minutes

    async def connect(self):
        """Connect to Redis."""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.redis:
            return None
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if not self.redis:
            return False
        ttl = ttl or self.default_ttl
        serialized = json.dumps(value) if not isinstance(value, str) else value
        return await self.redis.setex(key, ttl, serialized)

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.redis:
            return False
        return bool(await self.redis.delete(key))

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis:
            return 0
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis:
            return False
        return bool(await self.redis.exists(key))

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter."""
        if not self.redis:
            return 0
        return await self.redis.incrby(key, amount)

    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement a counter."""
        if not self.redis:
            return 0
        return await self.redis.decrby(key, amount)


# Global cache instance
cache_service = CacheService()


def cached(
    key_prefix: str,
    ttl: Optional[int] = None,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds (optional)
        key_builder: Custom function to build cache key from args
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Simple key from arguments
                arg_str = "_".join(str(arg) for arg in args if arg)
                kwarg_str = "_".join(f"{k}_{v}" for k, v in kwargs.items())
                cache_key = f"{key_prefix}:{arg_str}:{kwarg_str}"

            # Try to get from cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            await cache_service.set(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def invalidate_pattern(pattern: str):
    """
    Decorator to invalidate cache patterns after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate (e.g., "conversations:*")
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            await cache_service.delete_pattern(pattern)
            return result
        return wrapper
    return decorator
