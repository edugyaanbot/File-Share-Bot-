from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu keyboard"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📤 Upload File"),
        KeyboardButton(text="📂 My Files")
    )
    builder.row(
        KeyboardButton(text="❓ Help")
    )
    return builder.as_markup(resize_keyboard=True)


def get_file_link_keyboard(deep_link: str) -> InlineKeyboardMarkup:
    """Get keyboard with file link"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔗 Open Link", url=deep_link)
    )
    return builder.as_markup()


def get_file_actions_keyboard(uuid: str, deep_link: str) -> InlineKeyboardMarkup:
    """Get keyboard for file actions"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔗 Open Link", url=deep_link)
    )
    builder.row(
        InlineKeyboardButton(text="📱 Show QR", callback_data=f"file:qr:{uuid}")
    )
    return builder.as_markup()
