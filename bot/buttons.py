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
per = InlineKeyboardButton(text="For one game", callback_data="per")
three = InlineKeyboardButton(text="For three games", callback_data="three")
per_or_team_button = InlineKeyboardMarkup(row_width=1).add(per, three)

just_for_me = InlineKeyboardButton(text="For me only", callback_data="only_me")
for_team = InlineKeyboardButton(text="For Team", callback_data="for_team")
who_button = InlineKeyboardMarkup(row_width=1).add(just_for_me, for_team)

change = InlineKeyboardButton(
    text="Change Team",
    callback_data="change_team"
)

change_team = InlineKeyboardMarkup().add(change, pay_game)

change_team1 = InlineKeyboardMarkup().add(change)

# def play_button_markup(data):
play = InlineKeyboardButton(text="Play", callback_data="play")
payed_button = InlineKeyboardMarkup(row_width=1).add(play, go_back)
# return payed_button
