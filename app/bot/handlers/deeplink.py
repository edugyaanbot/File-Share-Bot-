from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
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
    try:
        # Extract UUID from deep link
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            logger.warning(f"Invalid deep link format: {message.text}")
            await message.answer("❌ Invalid link format")
            return
        
        uuid = args[1].strip()
        logger.info(f"Processing deep link request for UUID: {uuid}")
        
        # Find file
        file_doc = await get_file_by_uuid(uuid)
        
        if not file_doc:
            logger.warning(f"File not found: {uuid}")
            await message.answer("❌ File not found")
            return
        
        logger.info(f"File found: {uuid}, type: {file_doc['type']}, owner: {file_doc['owner_id']}")
        
        # Check if deleted
        if file_doc.get("deleted_at"):
            logger.warning(f"File is deleted: {uuid}")
            await message.answer("❌ This file has been deleted")
            return
        
        # Check if owner is banned
        if await is_user_banned(file_doc["owner_id"]):
            logger.warning(f"File owner is banned: {file_doc['owner_id']}")
            await message.answer("❌ This file is no longer available")
            return
        
        # Copy message from storage channel
        logger.info(f"Attempting to copy message {file_doc['storage_channel_message_id']} from channel {settings.STORAGE_CHANNEL_ID}")
        
        try:
            # Prepare caption
            file_name = file_doc.get('file_name', 'File')
            file_size = humanize_bytes(file_doc['size_bytes'])
            caption_text = f"📁 <b>{file_name}</b>\n💾 Size: {file_size}\n📥 Downloads: {file_doc['downloads']}"
            
            # Copy the message
            copied_message = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=settings.STORAGE_CHANNEL_ID,
                message_id=file_doc["storage_channel_message_id"],
                caption=caption_text,
                parse_mode="HTML"
            )
            
            logger.info(f"Successfully copied message {copied_message.message_id} to user {message.from_user.id}")
            
            # Increment downloads
            await increment_downloads(uuid)
            
            # Log audit
            await log_audit(message.from_user.id, "FILE_SERVED", uuid)
            
            # Send action buttons
            deep_link = f"https://t.me/{settings.BOT_USERNAME}?start={uuid}"
            await message.answer(
                "✅ <b>File retrieved successfully!</b>\n\n"
                "Use the buttons below for more options:",
                reply_markup=get_file_actions_keyboard(uuid, deep_link),
                parse_mode="HTML"
            )
            
            logger.info(f"File {uuid} delivered to user {message.from_user.id}")
            
        except Exception as copy_error:
            logger.error(f"Error copying message from storage channel: {copy_error}", exc_info=True)
            await message.answer(
                "❌ <b>Error retrieving file</b>\n\n"
                "The file may have been deleted from storage or the bot doesn't have access to the storage channel.\n\n"
                "Please contact the file owner.",
                parse_mode="HTML"
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in deep link handler: {e}", exc_info=True)
        await message.answer(
            "❌ <b>An error occurred</b>\n\n"
            "Please try again or contact support.",
            parse_mode="HTML"
        )


@router.callback_query(F.data.startswith("file:qr:"))
async def send_qr_again(callback: CallbackQuery, bot: Bot):
    """Send QR code with spoiler"""
    try:
        uuid = callback.data.split(":")[2]
        logger.info(f"Generating QR code for {uuid}")
        
        qr_file = await generate_qr_code(uuid)
        
        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=qr_file,
            caption="📱 <b>Scan this QR code to access the file</b>\n<i>(tap to reveal)</i>",
            has_spoiler=True,
            parse_mode="HTML"
        )
        
        logger.info(f"QR code sent for {uuid}")
        await callback.answer("✅ QR code sent!")
        
    except Exception as e:
        logger.error(f"Error sending QR code: {e}", exc_info=True)
        await callback.answer("❌ Error generating QR code", show_alert=True)
