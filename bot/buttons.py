from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

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
per = InlineKeyboardButton(text="За одну игру", callback_data="per")
three = InlineKeyboardButton(text="За три игры", callback_data="three")
per_or_three_button = InlineKeyboardMarkup(row_width=1).add(per, three)

change = InlineKeyboardButton(
    text="Изменить игру",
    callback_data="change_team"
)

button = InlineKeyboardButton(
    text="я принимаю правила",
    callback_data="rules"
)
btn = InlineKeyboardMarkup().add(button)


def change_team(callback_data):
    var = InlineKeyboardButton("Не смогу придти", callback_data=f"absence:{callback_data}")
    return InlineKeyboardMarkup(row_width=2).add(change, pay_game, var)


change_team1 = InlineKeyboardMarkup().add(change)

# def play_button_markup(data):
play = InlineKeyboardButton(text="Присоеденится", callback_data="play")
payed_button = InlineKeyboardMarkup(row_width=1).add(play, go_back)
# return payed_button
