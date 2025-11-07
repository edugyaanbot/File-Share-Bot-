from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.services.files import get_user_files, count_user_files, soft_delete_file, get_file_by_uuid
from app.bot.keyboards.myfiles import get_myfiles_keyboard, get_file_detail_keyboard
from app.config import settings
from app.utils.helpers import humanize_bytes
import math
import logging

router = Router()
logger = logging.getLogger(__name__)

PAGE_SIZE = 10


@router.message(Command("myfiles"))
async def cmd_myfiles(message: Message):
    """Handle /myfiles command"""
    await show_myfiles_page(message, message.from_user.id, 1)


async def show_myfiles_page(message: Message, user_id: int, page: int):
    """Show paginated files list"""
    files = await get_user_files(user_id, page, PAGE_SIZE)
    total_files = await count_user_files(user_id)
    total_pages = math.ceil(total_files / PAGE_SIZE) if total_files > 0 else 1
    
    if not files:
        await message.answer(
            "📂 <b>My Files</b>\n\n"
            "You haven't uploaded any files yet.\n"
            "Send me a file to get started!"
        )
        return
    
    text = f"📂 <b>My Files</b> (Page {page}/{total_pages})\n\n"
    text += f"Total: {total_files} files\n\n"
    text += "Tap a file to view details:"
    
    await message.answer(
        text,
        reply_markup=get_myfiles_keyboard(files, page, total_pages)
    )


@router.callback_query(F.data.startswith("myfiles:page:"))
async def myfiles_pagination(callback: CallbackQuery):
    """Handle pagination"""
    page = int(callback.data.split(":")[2])
    
    files = await get_user_files(callback.from_user.id, page, PAGE_SIZE)
    total_files = await count_user_files(callback.from_user.id)
    total_pages = math.ceil(total_files / PAGE_SIZE) if total_files > 0 else 1
    
    text = f"📂 <b>My Files</b> (Page {page}/{total_pages})\n\n"
    text += f"Total: {total_files} files\n\n"
    text += "Tap a file to view details:"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_myfiles_keyboard(files, page, total_pages)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file:view:"))
async def view_file_detail(callback: CallbackQuery):
    """Show file details"""
    uuid = callback.data.split(":")[2]
    
    file_doc = await get_file_by_uuid(uuid)
    
    if not file_doc or file_doc.get("deleted_at"):
        await callback.answer("❌ File not found", show_alert=True)
        return
    
    deep_link = f"https://t.me/{settings.BOT_USERNAME}?start={uuid}"
    
    text = (
        f"📄 <b>{file_doc.get('file_name', 'Unnamed')}</b>\n\n"
        f"🔹 Type: {file_doc['type'].title()}\n"
        f"🔹 Size: {humanize_bytes(file_doc['size_bytes'])}\n"
        f"🔹 Downloads: {file_doc['downloads']}\n"
        f"🔹 Created: {file_doc['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
        f"🔗 Link:\n<code>{deep_link}</code>"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_file_detail_keyboard(uuid, deep_link)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("file:delete:"))
async def delete_file_confirm(callback: CallbackQuery):
    """Delete file"""
    uuid = callback.data.split(":")[2]
    
    file_doc = await get_file_by_uuid(uuid)
    
    if not file_doc:
        await callback.answer("❌ File not found", show_alert=True)
        return
    
    if file_doc["owner_id"] != callback.from_user.id:
        await callback.answer("❌ Not your file", show_alert=True)
        return
    
    await soft_delete_file(uuid, callback.from_user.id)
    
    await callback.message.edit_text(
        "🗑 <b>File Deleted</b>\n\n"
        "The file has been removed from your list and is no longer accessible."
    )
    await callback.answer("✅ File deleted")


@router.callback_query(F.data == "myfiles:noop")
async def noop_callback(callback: CallbackQuery):
    """No-op callback for current page display"""
    await callback.answer()
