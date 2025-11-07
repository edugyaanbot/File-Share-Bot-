from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from app.bot.keyboards.main_menu import get_main_menu
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: Message):
    """Handle /start command without deep link"""
    welcome_text = (
        "👋 <b>Welcome to File Share Bot!</b>\n\n"
        "📤 Send me any file, photo, video, voice, or document.\n"
        "🔐 I'll store it privately and give you:\n"
        "   • Shareable link\n"
        "   • QR code (with spoiler effect)\n\n"
        "✨ Your files are stored securely and accessible anytime!"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "📖 <b>How to use:</b>\n\n"
        "1️⃣ Send me any file\n"
        "2️⃣ Get a shareable link and QR code\n"
        "3️⃣ Share with anyone!\n\n"
        "📂 /myfiles - View your uploaded files\n"
        "❓ /help - Show this message"
    )
    
    await message.answer(help_text)


@router.message(F.text == "❓ Help")
async def help_button(message: Message):
    """Handle Help button"""
    await cmd_help(message)


@router.message(F.text == "📤 Upload File")
async def upload_button(message: Message):
    """Handle Upload button"""
    await message.answer(
        "📤 Send me any file to upload!\n\n"
        "Supported: Documents, Photos, Videos, Audio, Voice messages"
    )
