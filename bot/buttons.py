from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from bot.sheet_read import normalize_data, read_sheet_values
from auth import get_credentials

list_of_buttons = []
keys = ["id", "date", "weekday", "address", "time"]
for text in normalize_data(read_sheet_values(table_name="Расписание!A1:G",keys=keys)):
    list_of_buttons.append(InlineKeyboardButton(text="Записаться", callback_data="Example"))

pay_game = InlineKeyboardButton("Pay for a game")
go_back = InlineKeyboardButton("Go back to list")
play_button = InlineKeyboardButton("Wanna play")

register_buttons = InlineKeyboardMarkup().add(pay_game, go_back, play_button)
keyboard = InlineKeyboardMarkup().add(*list_of_buttons)
