"""Redis caching utilities."""
import json
import pickle
from typing import Any, Optional, Callable
from functools import wraps
import redis.asyncio as aioredis
from app.config import settings


class CacheManager:
    """Redis cache manager for the application."""
    
    def __init__(self):
        """Initialize cache manager."""
        self._redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self._redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False
            )
            # Test connection
            await self._redis.ping()
            print(f"✓ Connected to Redis at {settings.REDIS_URL}")
        except Exception as e:
            print(f"✗ Failed to connect to Redis: {e}")
            print("  Cache will be disabled")
            self._redis = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._redis:
            await self._redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value:
                return pickle.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = 300
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        if not self._redis:
            return False
        
        try:
            serialized = pickle.dumps(value)
            if ttl:
                await self._redis.setex(key, ttl, serialized)
            else:
                await self._redis.set(key, serialized)
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis:
            return False
        
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "conversation:*")
        
        Returns:
            Number of keys deleted
        """
        if not self._redis:
            return 0
        
        try:
            keys = []
            async for key in self._redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self._redis:
            return False
        
        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            print(f"Cache exists error for key {key}: {e}")
            return False


# Global cache instance
cache = CacheManager()


def cached(
    key_prefix: str,
    ttl: int = 300,
    key_builder: Optional[Callable] = None
):
    """
    Decorator for caching function results.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        key_builder: Optional function to build cache key from args
    
    Example:
        @cached("conversation", ttl=600)
        async def get_conversation(conversation_id: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                # Use function args to build key
                key_parts = [str(arg) for arg in args]
                key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
                cache_key = f"{key_prefix}:{'_'.join(key_parts)}"
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


async def invalidate_conversation_cache(conversation_id: str):
    """Invalidate all cache entries for a conversation."""
    await cache.delete_pattern(f"conversation:{conversation_id}:*")
    await cache.delete(f"conversation:{conversation_id}")


async def invalidate_analytics_cache():
    """Invalidate analytics cache."""
    await cache.delete_pattern("analytics:*")
    await cache.delete_pattern("timeline:*")


async def invalidate_intelligence_cache(conversation_id: Optional[str] = None):
    """Invalidate intelligence cache."""
    if conversation_id:
        await cache.delete_pattern(f"intelligence:conversation:{conversation_id}:*")
    else:
        await cache.delete_pattern("intelligence:*")
