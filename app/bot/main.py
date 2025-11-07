from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.bot.handlers import start, deeplink, upload, myfiles, admin
from app.bot.middlewares.auth import AuthMiddleware
from app.bot.middlewares.rate_limit import RateLimitMiddleware
from app.bot.middlewares.logging_middleware import LoggingMiddleware
import logging

logger = logging.getLogger(__name__)

bot: Bot = None
dp: Dispatcher = None


async def setup_bot():
    """Setup bot and webhook"""
    global bot, dp
    
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    
    # Register middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    
    # Register routers - ORDER MATTERS!
    # Deep link MUST be before regular start handler
    dp.include_router(deeplink.router)  # First - handles /start with UUID
    dp.include_router(start.router)     # Second - handles /start without UUID
    dp.include_router(upload.router)
    dp.include_router(myfiles.router)
    dp.include_router(admin.router)
    
    # Set webhook
    webhook_url = f"{settings.WEBHOOK_BASE_URL}/webhook"
    
    try:
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        logger.info(f"✅ Webhook set to {webhook_url}")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")
        raise


def get_bot() -> Bot:
    """Get bot instance"""
    return bot


def get_bot_dispatcher() -> Dispatcher:
    """Get dispatcher instance"""
    return dp
