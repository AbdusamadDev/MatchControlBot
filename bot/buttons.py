from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.sheet_read import normalize_data, read_sheet_values
from auth import get_credentials

list_of_buttons = []
keys = ["id", "date", "weekday", "address", "time"]
for text in normalize_data(read_sheet_values(table_name="Расписание!A1:G", keys=keys)):
    list_of_buttons.append(InlineKeyboardButton(text="Записаться", callback_data=f"Example:{text}"))

pay_game = InlineKeyboardButton("Оплатить игру", callback_data="pay_game")
go_back = InlineKeyboardButton("Вернуться к списку матчей", callback_data="go_back")
play_button = InlineKeyboardButton("Хочу играть", callback_data="play_button")

but1 = KeyboardButton(text="Записаться на игру")
but2 = KeyboardButton(text="Моя команда")
two_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(but1, but2)

register_buttons = InlineKeyboardMarkup(row_width=2).add(pay_game, play_button, go_back)
keyboard = InlineKeyboardMarkup(resize_keyboard=True).add(*list_of_buttons)
