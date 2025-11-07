import redis.asyncio as redis
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    if settings.REDIS_URL:
        try:
            redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,
                socket_connect_timeout=5
            )
            await redis_client.ping()
            logger.info("✅ Redis client initialized")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Caching disabled.")
            redis_client = None
    else:
        logger.warning("⚠️ Redis URL not configured, caching disabled")


async def close_redis():
    """Close Redis connection"""
    if redis_client:
        await redis_client.close()
        logger.info("Redis client closed")


async def cache_get(key: str) -> Optional[bytes]:
    """Get value from cache"""
    if not redis_client:
        return None
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None


async def cache_set(key: str, value: bytes, ttl: int = 3600):
    """Set value in cache with TTL"""
    if not redis_client:
        return
    try:
        await redis_client.setex(key, ttl, value)
    except Exception as e:
        logger.error(f"Cache set error: {e}")


async def cache_delete(key: str):
    """Delete key from cache"""
    if not redis_client:
        return
    try:
        await redis_client.delete(key)
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
