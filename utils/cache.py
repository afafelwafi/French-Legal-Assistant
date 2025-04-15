# utils/cache.py
import json
import redis
import hashlib
from typing import Any, Optional, Dict
import os


class RedisCache:
    """Cache implementation using Redis."""

    def __init__(self, prefix: str = "legal_assistant"):
        """
        Initialize the Redis cache.

        Args:
            prefix: Prefix for cache keys
        """
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.prefix = prefix
        self.ttl = int(os.getenv("CACHE_TTL", 86400))  # Default: 1 day

        # Connect to Redis
        self.redis = redis.Redis(
            host=self.redis_host, port=self.redis_port, decode_responses=True
        )

    def _generate_key(self, key_params: Dict[str, Any]) -> str:
        """
        Generate a cache key from parameters.

        Args:
            key_params: Parameters to include in the key

        Returns:
            String cache key
        """
        # Convert parameters to string and hash
        param_str = json.dumps(key_params, sort_keys=True)
        key_hash = hashlib.md5(param_str.encode()).hexdigest()

        return f"{self.prefix}:{key_hash}"

    def get(self, key_params: Dict[str, Any]) -> Optional[str]:
        """
        Get a value from the cache.

        Args:
            key_params: Parameters to generate the key

        Returns:
            Cached value or None if not found
        """
        key = self._generate_key(key_params)
        try:
            return self.redis.get(key)
        except redis.RedisError:
            # Log error but continue without cache
            return None

    def set(self, key_params: Dict[str, Any], value: str, ttl: int = None) -> bool:
        """
        Set a value in the cache.

        Args:
            key_params: Parameters to generate the key
            value: Value to cache
            ttl: Time to live in seconds (None for default)

        Returns:
            True if successful
        """
        key = self._generate_key(key_params)
        try:
            return self.redis.set(key, value, ex=(ttl or self.ttl))
        except redis.RedisError:
            # Log error but continue without cache
            return False

    def delete(self, key_params: Dict[str, Any]) -> bool:
        """
        Delete a value from the cache.

        Args:
            key_params: Parameters to generate the key

        Returns:
            True if successful
        """
        key = self._generate_key(key_params)
        try:
            return bool(self.redis.delete(key))
        except redis.RedisError:
            # Log error but continue without cache
            return False

    def flush(self, pattern: str = None) -> int:
        """
        Flush all keys matching the pattern.

        Args:
            pattern: Pattern to match (None for all keys with prefix)

        Returns:
            Number of keys deleted
        """
        pattern = pattern or f"{self.prefix}:*"
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except redis.RedisError:
            # Log error but continue without cache
            return 0
