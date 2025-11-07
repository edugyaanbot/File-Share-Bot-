from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from app.bot.keyboards.admin import get_admin_menu
from app.services.stats import get_dashboard_stats
from app.config import settings
import logging

router = Router()
logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.admin_ids_list


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Handle /admin command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied. Admin only.")
        return
    
    await message.answer(
        "⚙️ <b>Admin Panel</b>\n\n"
        "Choose an option:",
        reply_markup=get_admin_menu()
    )


@router.callback_query(F.data == "admin:stats")
async def show_admin_stats(callback: CallbackQuery):
    """Show statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    stats = await get_dashboard_stats()
    
    text = (
        "📊 <b>Statistics</b>\n\n"
        f"👥 <b>Users</b>\n"
        f"├ Total: {stats['total_users']}\n"
        f"├ Active (24h): {stats['active_24h']}\n"
        f"├ New (24h): {stats['new_24h']}\n"
        f"└ Banned: {stats['banned_users']}\n\n"
        f"📁 <b>Files</b>\n"
        f"├ Total: {stats['total_files']}\n"
        f"├ Created (24h): {stats['files_24h']}\n"
        f"├ Deleted: {stats['deleted_files']}\n"
        f"└ Storage: {stats['storage_human']}\n\n"
        f"🔥 <b>Top Files</b>\n"
    )
    
    for i, file in enumerate(stats['top_files'][:5], 1):
        text += f"{i}. {file['file_name'][:20]} - {file['downloads']} downloads\n"
    
    await callback.message.edit_text(text)
    await callback.answer()


@router.callback_query(F.data == "admin:users")
async def show_admin_users(callback: CallbackQuery):
    """Show users management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await callback.message.edit_text(
        "👥 <b>User Management</b>\n\n"
        "Use the web admin panel for full user management:\n"
        f"{settings.WEBHOOK_BASE_URL}/admin"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:files")
async def show_admin_files(callback: CallbackQuery):
    """Show files management"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📁 <b>File Management</b>\n\n"
        "Use the web admin panel for full file management:\n"
        f"{settings.WEBHOOK_BASE_URL}/admin"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:broadcast")
async def show_admin_broadcast(callback: CallbackQuery):
    """Show broadcast"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 <b>Broadcast</b>\n\n"
        "Use the web admin panel for broadcasting:\n"
        f"{settings.WEBHOOK_BASE_URL}/admin"
    )
    await callback.answer()


@router.callback_query(F.data == "admin:settings")
async def show_admin_settings(callback: CallbackQuery):
    """Show settings"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⚙️ <b>Settings</b>\n\n"
        f"Maintenance Mode: {'🔴 ON' if settings.MAINTENANCE_MODE else '🟢 OFF'}\n"
        f"Max File Size: {settings.MAX_FILE_SIZE_MB} MB\n"
        f"Rate Limit: {settings.USER_RATE_LIMIT_PER_MIN}/min\n\n"
        "Use the web admin panel for full settings:\n"
        f"{settings.WEBHOOK_BASE_URL}/admin"
    )
    await callback.answer()
