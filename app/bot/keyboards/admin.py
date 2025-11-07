from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_admin_menu() -> InlineKeyboardMarkup:
    """Get admin menu keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📊 Statistics", callback_data="admin:stats")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Users", callback_data="admin:users"),
        InlineKeyboardButton(text="📁 Files", callback_data="admin:files")
    )
    builder.row(
        InlineKeyboardButton(text="📢 Broadcast", callback_data="admin:broadcast"),
        InlineKeyboardButton(text="⚙️ Settings", callback_data="admin:settings")
    )
    
    return builder.as_markup()
