from app.services.cache import redis_client
from app.config import settings
import time
import logging

logger = logging.getLogger(__name__)


async def check_rate_limit(user_id: int) -> bool:
    """Check if user is within rate limit using sliding window"""
    if not redis_client:
        return True
    
    key = f"ratelimit:user:{user_id}"
    now = int(time.time())
    window = 60  # 1 minute
    
    try:
        # Remove old entries
        await redis_client.zremrangebyscore(key, 0, now - window)
        
        # Count requests in window
        count = await redis_client.zcard(key)
        
        if count >= settings.USER_RATE_LIMIT_PER_MIN:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False
        
        # Add current request
        await redis_client.zadd(key, {str(now): now})
        await redis_client.expire(key, window)
        
        return True
    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True


async def check_global_rate_limit() -> bool:
    """Check global rate limit"""
    if not redis_client:
        return True
    
    key = "ratelimit:global"
    now = int(time.time())
    
    try:
        await redis_client.zremrangebyscore(key, 0, now - 1)
        count = await redis_client.zcard(key)
        
        if count >= settings.GLOBAL_RATE_LIMIT_RPS:
            return False
        
        await redis_client.zadd(key, {f"{now}:{count}": now})
        await redis_client.expire(key, 2)
        
        return True
    except Exception as e:
        logger.error(f"Global rate limit error: {e}")
        return True
