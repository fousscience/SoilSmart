# app/core/cache.py
import json
import hashlib
from typing import Optional, Any
import os

# Try to import Redis, fallback to in-memory cache
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings

class Cache:
    """Cache system with Redis backend and in-memory fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}  # Fallback in-memory cache
        
        if REDIS_AVAILABLE and settings.REDIS_HOST:
            try:
                # Support for Redis URL format (e.g., from Render or Upstash)
                if settings.REDIS_HOST.startswith("redis://") or settings.REDIS_HOST.startswith("rediss://"):
                    # Use URL format
                    self.redis_client = redis.from_url(
                        settings.REDIS_HOST,
                        decode_responses=True,
                        socket_connect_timeout=2,
                        socket_timeout=2
                    )
                else:
                    # Use host/port format
                    self.redis_client = redis.Redis(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        password=settings.REDIS_PASSWORD,
                        decode_responses=True,
                        socket_connect_timeout=2,
                        socket_timeout=2
                    )
                # Test connection
                self.redis_client.ping()
                print("✅ Redis cache connected")
            except Exception as e:
                print(f"⚠️ Redis not available, using in-memory cache: {e}")
                self.redis_client = None
    
    @staticmethod
    def _generate_key(prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        key_str = ":".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"⚠️ Redis get error: {e}")
        
        # Fallback to memory cache
        return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        ttl = ttl or settings.REDIS_TTL
        value_str = json.dumps(value, ensure_ascii=False)
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, value_str)
                return True
            except Exception as e:
                print(f"⚠️ Redis set error: {e}")
        
        # Fallback to memory cache (limit size to prevent memory issues)
        if len(self.memory_cache) < 100:  # Limit to 100 entries
            self.memory_cache[key] = value
            return True
        return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception:
                pass
        
        # Fallback to memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            return True
        return False
    
    def clear(self):
        """Clear all cache"""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception:
                pass
        self.memory_cache.clear()

# Global cache instance
cache = Cache()

