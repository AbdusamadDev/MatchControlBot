from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from bot.sheet_read import normalize_data, read_sheet_values
from auth import get_credentials

list_of_buttons = []

for text in normalize_data(read_sheet_values(credentials=get_credentials())):
    list_of_buttons.append(InlineKeyboardButton(text="Записаться", callback_data="Example"))

keyboard = InlineKeyboardMarkup().add(*list_of_buttons)
