from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from app.services.files import get_file_by_uuid, increment_downloads
from app.services.users import is_user_banned
from app.services.audits import log_audit
from app.services.qr import generate_qr_code
from app.bot.keyboards.main_menu import get_file_actions_keyboard
from app.config import settings
from app.utils.helpers import humanize_bytes
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart(deep_link=True))
async def handle_deep_link(message: Message, bot: Bot):
    """Handle deep link to retrieve file"""
    # Extract UUID from deep link
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Invalid link")
        return
    
    uuid = args[1]
    
    # Find file
    file_doc = await get_file_by_uuid(uuid)
    
    if not file_doc:
        await message.answer("❌ File not found")
        return
    
    # Check if deleted
    if file_doc.get("deleted_at"):
        await message.answer("❌ This file has been deleted")
        return
    
    # Check if owner is banned
    if await is_user_banned(file_doc["owner_id"]):
        await message.answer("❌ This file is no longer available")
        return
    
    # Copy message from storage channel
    try:
        caption_text = f"📁 {file_doc.get('file_name', 'File')}\n💾 {humanize_bytes(file_doc['size_bytes'])}"
        
        await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=settings.STORAGE_CHANNEL_ID,
            message_id=file_doc["storage_channel_message_id"],
            caption=caption_text if file_doc['type'] != 'document' else None
        )
        
        # Increment downloads
        await increment_downloads(uuid)
        
        # Log audit
        await log_audit(message.from_user.id, "FILE_SERVED", uuid)
        
        # Send action buttons
        deep_link = f"https://t.me/{settings.BOT_USERNAME}?start={uuid}"
        await message.answer(
            "✅ File retrieved successfully!",
            reply_markup=get_file_actions_keyboard(uuid, deep_link)
        )
        
        logger.info(f"File {uuid} served to user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error copying file {uuid}: {e}")
        await message.answer("❌ Error retrieving file. It may have been deleted from storage.")


@router.callback_query(F.data.startswith("file:qr:"))
async def send_qr_again(callback: CallbackQuery, bot: Bot):
    """Send QR code with spoiler"""
    uuid = callback.data.split(":")[2]
    
    try:
        qr_buffer = await generate_qr_code(uuid)
        
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=qr_buffer,
            caption="📱 Scan this QR code to access the file",
            has_spoiler=True
        )
        
        await callback.answer("QR code sent!")
    except Exception as e:
        logger.error(f"Error sending QR for {uuid}: {e}")
        await callback.answer("❌ Error generating QR code", show_alert=True)
