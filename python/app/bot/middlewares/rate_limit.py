from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from app.services.rate_limit import check_rate_limit, check_global_rate_limit


class RateLimitMiddleware(BaseMiddleware):
    """Rate limiting middleware"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Check rate limits"""
        # Check global rate limit
        if not await check_global_rate_limit():
            await event.answer("⏳ Server is busy. Please try again later.")
            return
        
        # Check user rate limit
        if not await check_rate_limit(event.from_user.id):
            await event.answer("⏳ Please slow down. Try again in a minute.")
            return
        
        return await handler(event, data)
