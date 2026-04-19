"""Redis configuration for caching and distributed rate limiting."""
import os
from typing import Optional

import redis
from functools import lru_cache


class RedisConfig:
    """Redis configuration management."""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis_rate_limit_url = os.getenv(
            "REDIS_RATE_LIMIT_URL", 
            os.getenv("REDIS_URL", "redis://localhost:6379/0")
        )
    
    def get_redis_client(self, db: int = 0) -> redis.Redis:
        """Get Redis client for general use."""
        return redis.Redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
        )
    
    def get_rate_limit_redis(self) -> redis.Redis:
        """Get Redis client specifically for rate limiting."""
        return redis.Redis.from_url(
            self.redis_rate_limit_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
        )


@lru_cache()
def get_redis_config() -> RedisConfig:
    """Get cached Redis configuration."""
    return RedisConfig()


# Global Redis clients (initialized on first use)
_redis_client: Optional[redis.Redis] = None
_rate_limit_redis: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """Get or create Redis client."""
    global _redis_client
    if _redis_client is None:
        config = get_redis_config()
        _redis_client = config.get_redis_client()
    return _redis_client


def get_rate_limit_redis() -> redis.Redis:
    """Get or create rate limit Redis client."""
    global _rate_limit_redis
    if _rate_limit_redis is None:
        config = get_redis_config()
        _rate_limit_redis = config.get_rate_limit_redis()
    return _rate_limit_redis


def check_redis_connection() -> bool:
    """Check if Redis is connected and available."""
    try:
        redis_client = get_redis()
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False


# Cache decorators for common operations

def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from prefix and arguments."""
    key_parts = [prefix]
    key_parts.extend(str(arg) for arg in args)
    key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    return ":".join(key_parts)


def get_cached(key: str) -> Optional[str]:
    """Get value from cache."""
    try:
        return get_redis().get(key)
    except Exception:
        return None


def set_cached(key: str, value: str, expire_seconds: int = 300) -> bool:
    """Set value in cache with expiration."""
    try:
        get_redis().setex(key, expire_seconds, value)
        return True
    except Exception:
        return False


def delete_cached(key: str) -> bool:
    """Delete value from cache."""
    try:
        get_redis().delete(key)
        return True
    except Exception:
        return False


def invalidate_pattern(pattern: str) -> int:
    """Delete all keys matching pattern."""
    try:
        redis_client = get_redis()
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception:
        return 0
