from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

pay_game = InlineKeyboardButton("Оплатить игру", callback_data="pay_game")
go_back = InlineKeyboardButton("Вернуться к списку матчей", callback_data="go_back")
play_button = InlineKeyboardButton("Хочу играть", callback_data="play_button")

but1 = KeyboardButton(text="Записаться на игру")
but2 = KeyboardButton(text="Моя команда")
two_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(but1, but2)


def absence(callback_data):
    absence_b = InlineKeyboardButton("Не смогу придти", callback_data=f"absence:{callback_data}")
    return InlineKeyboardMarkup().add(absence_b)


register_buttons = InlineKeyboardMarkup(row_width=2).add(pay_game, play_button, go_back)
per = InlineKeyboardButton(text="За себя", callback_data="per")
three = InlineKeyboardButton(text="За команду", callback_data="team")
per_or_team_button = InlineKeyboardMarkup(row_width=1).add(per, three)
