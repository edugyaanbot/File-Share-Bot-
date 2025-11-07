from aiogram import Router, F, Bot
from aiogram.types import Message, ContentType
from app.services.files import create_file_record
from app.services.qr import generate_qr_code
from app.bot.keyboards.main_menu import get_file_link_keyboard
from app.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.content_type.in_([
    ContentType.DOCUMENT,
    ContentType.PHOTO,
    ContentType.VIDEO,
    ContentType.AUDIO,
    ContentType.VOICE,
    ContentType.ANIMATION,
    ContentType.STICKER
]))
async def handle_file_upload(message: Message, bot: Bot):
    """Handle file upload from user"""
    user_id = message.from_user.id
    
    # Extract file metadata
    file_type, file_obj = extract_file_info(message)
    
    if not file_obj:
        await message.answer("❌ Unable to process this file type")
        return
    
    # Check file size
    file_size = getattr(file_obj, 'file_size', 0)
    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    
    if file_size > max_size:
        await message.answer(f"❌ File too large. Max: {settings.MAX_FILE_SIZE_MB} MB")
        return
    
    # Show processing message
    status_msg = await message.answer("⏳ Processing your file...")
    
    # Copy to storage channel (not forward)
    try:
        copied = await bot.copy_message(
            chat_id=settings.STORAGE_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        
        # Create file record
        file_doc = await create_file_record(
            owner_id=user_id,
            file_type=file_type,
            storage_message_id=copied.message_id,
            file_id=file_obj.file_id,
            file_unique_id=file_obj.file_unique_id,
            file_name=getattr(file_obj, 'file_name', None),
            mime_type=getattr(file_obj, 'mime_type', None),
            size_bytes=file_size,
            width=getattr(file_obj, 'width', None),
            height=getattr(file_obj, 'height', None)
        )
        
        uuid = file_doc["uuid"]
        deep_link = f"https://t.me/{settings.BOT_USERNAME}?start={uuid}"
        
        # Delete processing message
        await status_msg.delete()
        
        # Send success message with link
        await message.answer(
            f"✅ <b>Stored Successfully!</b>\n\n"
            f"📎 Share this link:\n<code>{deep_link}</code>",
            reply_markup=get_file_link_keyboard(deep_link)
        )
        
        # Generate and send QR with spoiler
        qr_buffer = await generate_qr_code(uuid)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=qr_buffer,
            caption="📱 Scan QR to retrieve file (tap to reveal)",
            has_spoiler=True,
            disable_notification=True
        )
        
        logger.info(f"File {uuid} uploaded by user {user_id}")
        
    except Exception as e:
        logger.error(f"Error storing file: {e}")
        await status_msg.edit_text("❌ Error storing file. Please try again.")


def extract_file_info(message: Message):
    """Extract file information from message"""
    if message.document:
        return "document", message.document
    elif message.photo:
        return "photo", message.photo[-1]  # Largest photo
    elif message.video:
        return "video", message.video
    elif message.audio:
        return "audio", message.audio
    elif message.voice:
        return "voice", message.voice
    elif message.animation:
        return "animation", message.animation
    elif message.sticker:
        return "sticker", message.sticker
    return None, None


@router.message(F.text == "📂 My Files")
async def myfiles_button(message: Message):
    """Redirect to myfiles handler"""
    from app.bot.handlers.myfiles import cmd_myfiles
    await cmd_myfiles(message)
