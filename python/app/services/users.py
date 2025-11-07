from datetime import datetime
from typing import Optional, Dict, Any
from app.db.mongo import get_database
import logging

logger = logging.getLogger(__name__)


async def upsert_user(
    user_id: int,
    first_name: str,
    last_name: Optional[str],
    username: Optional[str]
) -> Dict[str, Any]:
    """Create or update user record"""
    db = get_database()
    
    now = datetime.utcnow()
    
    user_doc = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "last_seen_at": now
    }
    
    await db.users.update_one(
        {"user_id": user_id},
        {
            "$set": user_doc,
            "$setOnInsert": {
                "is_banned": False,
                "created_at": now
            }
        },
        upsert=True
    )
    
    user = await db.users.find_one({"user_id": user_id})
    return user


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    db = get_database()
    return await db.users.find_one({"user_id": user_id})


async def is_user_banned(user_id: int) -> bool:
    """Check if user is banned"""
    user = await get_user(user_id)
    return user.get("is_banned", False) if user else False


async def ban_user(user_id: int, actor_id: int):
    """Ban a user"""
    from app.services.audits import log_audit
    
    db = get_database()
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_banned": True}}
    )
    
    await log_audit(actor_id, "USER_BANNED", notes=f"Banned user {user_id}")
    logger.info(f"User {user_id} banned by {actor_id}")


async def unban_user(user_id: int, actor_id: int):
    """Unban a user"""
    from app.services.audits import log_audit
    
    db = get_database()
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_banned": False}}
    )
    
    await log_audit(actor_id, "USER_UNBANNED", notes=f"Unbanned user {user_id}")
    logger.info(f"User {user_id} unbanned by {actor_id}")
