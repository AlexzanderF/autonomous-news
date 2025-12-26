"""
Redis client utility for centralized Redis connection management.
Reuses the same configuration as Celery (from environment variables).
"""
import os
import redis
from typing import Optional

_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get a Redis client instance using environment configuration.
    Returns a singleton instance for connection reuse.
    """
    global _redis_client
    
    if _redis_client is None:
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', '6379'))
        db = int(os.getenv('REDIS_DB', '0'))
        password = os.getenv('REDIS_PASSWORD')
        
        _redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password if password else None,
            decode_responses=True
        )
    
    return _redis_client
