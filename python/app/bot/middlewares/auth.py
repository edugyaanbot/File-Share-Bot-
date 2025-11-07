from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from app.services.users import is_user_banned, upsert_user
from app.config import settings


class AuthMiddleware(BaseMiddleware):
    """Authentication middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Check if user is banned"""
        user = event.from_user
        
        # Upsert user on every interaction
        await upsert_user(
            user.id,
            user.first_name,
            user.last_name,
            user.username
        )
        
        # Check maintenance mode (admins bypass)
        if settings.MAINTENANCE_MODE and user.id not in settings.admin_ids_list:
            await event.answer("⚠️ Bot is under maintenance. Please try again later.")
            return
        
        # Check if banned
        if await is_user_banned(user.id):
            await event.answer("❌ You are banned from using this bot.")
            return
        
        return await handler(event, data)
