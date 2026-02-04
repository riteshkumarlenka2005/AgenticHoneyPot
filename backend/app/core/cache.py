"""Redis cache configuration and utilities."""
import json
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as redis
from app.config import settings


class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        """Initialize Redis connection pool."""
        self.redis: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None
    
    async def connect(self):
        """Connect to Redis."""
        if not self._pool:
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                max_connections=10
            )
            self.redis = redis.Redis(connection_pool=self._pool)
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
        if self._pool:
            await self._pool.disconnect()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        if not self.redis:
            await self.connect()
        return await self.redis.set(key, value, ex=expire)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from cache."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache."""
        json_value = json.dumps(value)
        return await self.set(key, json_value, expire)
    
    async def delete(self, key: str) -> int:
        """Delete key from cache."""
        if not self.redis:
            await self.connect()
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.redis:
            await self.connect()
        return bool(await self.redis.exists(key))
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.redis:
            await self.connect()
        
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0
    
    async def invalidate_conversation(self, conversation_id: str):
        """Invalidate all cache entries for a conversation."""
        await self.clear_pattern(f"conversation:{conversation_id}:*")
        await self.delete(f"conversation:{conversation_id}")
    
    async def invalidate_intelligence(self):
        """Invalidate intelligence cache."""
        await self.clear_pattern("intelligence:*")


# Global cache instance
cache = RedisCache()


def cached(
    key_pattern: str,
    expire: int = 300
):
    """
    Decorator for caching function results.
    
    Args:
        key_pattern: Redis key pattern (can use {arg_name} for function arguments)
        expire: Expiration time in seconds (default: 5 minutes)
    
    Example:
        @cached("user:{user_id}", expire=60)
        async def get_user(user_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from pattern and arguments
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            cache_key = key_pattern.format(**bound_args.arguments)
            
            # Try to get from cache
            cached_value = await cache.get_json(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set_json(cache_key, result, expire=expire)
            
            return result
        
        return wrapper
    return decorator


async def get_or_set_cache(
    key: str,
    fetch_func: Callable,
    expire: int = 300
) -> Any:
    """
    Get value from cache or execute function and cache result.
    
    Args:
        key: Redis key
        fetch_func: Async function to execute if cache miss
        expire: Expiration time in seconds
    
    Returns:
        Cached or fetched value
    """
    # Try cache first
    cached_value = await cache.get_json(key)
    if cached_value is not None:
        return cached_value
    
    # Fetch and cache
    value = await fetch_func()
    await cache.set_json(key, value, expire=expire)
    
    return value
