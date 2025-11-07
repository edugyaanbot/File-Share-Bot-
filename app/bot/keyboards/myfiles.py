from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict, Any


def get_myfiles_keyboard(files: List[Dict[str, Any]], page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Get keyboard for My Files list"""
    builder = InlineKeyboardBuilder()
    
    for file in files:
        uuid = file['uuid']
        name = file.get('file_name', 'Unnamed')[:30]
        
        builder.row(
            InlineKeyboardButton(text=f"📄 {name}", callback_data=f"file:view:{uuid}")
        )
    
    # Pagination
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"myfiles:page:{page-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="myfiles:noop"))
    
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"myfiles:page:{page+1}"))
    
    builder.row(*nav_buttons)
    
    return builder.as_markup()


def get_file_detail_keyboard(uuid: str, deep_link: str) -> InlineKeyboardMarkup:
    """Get keyboard for individual file details"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="🔗 Open", url=deep_link)
    )
    builder.row(
        InlineKeyboardButton(text="📱 QR", callback_data=f"file:qr:{uuid}"),
        InlineKeyboardButton(text="🗑 Delete", callback_data=f"file:delete:{uuid}")
    )
    builder.row(
        InlineKeyboardButton(text="« Back", callback_data="myfiles:page:1")
    )
    
    return builder.as_markup()
