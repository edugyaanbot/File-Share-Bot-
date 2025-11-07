from fastapi import APIRouter, Depends, BackgroundTasks
from app.web.auth import get_current_admin
from app.db.mongo import get_database
from app.bot.main import get_bot
from pydantic import BaseModel
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class BroadcastRequest(BaseModel):
    message: str
    parse_mode: str = "HTML"


async def send_broadcast(message: str, parse_mode: str):
    """Send broadcast to all users"""
    db = get_database()
    bot = get_bot()
    
    users = await db.users.find({"is_banned": False}).to_list(None)
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            await bot.send_message(
                chat_id=user['user_id'],
                text=message,
                parse_mode=parse_mode
            )
            success += 1
        except Exception as e:
            logger.error(f"Broadcast failed for user {user['user_id']}: {e}")
            failed += 1
    
    logger.info(f"Broadcast complete: {success} success, {failed} failed")


@router.post("/broadcast", dependencies=[Depends(get_current_admin)])
async def api_broadcast(request: BroadcastRequest, background_tasks: BackgroundTasks):
    """Send broadcast message"""
    background_tasks.add_task(send_broadcast, request.message, request.parse_mode)
    return {"status": "success", "message": "Broadcast started"}
