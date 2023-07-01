from sheet_read import read_sheet_values
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

pay_game = InlineKeyboardButton("Оплатить игру", callback_data="pay_game")
go_back = InlineKeyboardButton("Вернуться к списку матчей", callback_data="go_back")
play_button = InlineKeyboardButton("Хочу играть", callback_data="play_button")

but1 = KeyboardButton(text="Записаться на игру")
but2 = KeyboardButton(text="Мои игры")
but3 = KeyboardButton(text="Моя команда")
two_buttons = ReplyKeyboardMarkup(resize_keyboard=True).add(but1, but2, but3)

add = InlineKeyboardButton(text="Add teammates", callback_data="add")
delete = InlineKeyboardButton(text="Delete teammates", callback_data="delete")
cap_buttons = InlineKeyboardMarkup().add(add, delete)

me_only_button = InlineKeyboardButton("For me only", callback_data="personal_payment")
for_team_button = InlineKeyboardButton("For team payment", callback_data="team_payment")
payment_format_buttons = InlineKeyboardMarkup().add(me_only_button, for_team_button)

confirm = InlineKeyboardButton("Confirm and continue", callback_data="confirm")


# confirm_button = InlineKeyboardMarkup().add(*list_of_buttons, confirm)


def final_delete_button(text, call):
    final_delete = InlineKeyboardButton(text=text, callback_data="teammate:" + str(call))
    return final_delete


def get_designed_user(keys):
    users = read_sheet_values(
        table_name="Пользователи!A1:G",
        keys=keys
    )
    user_buttons = []
    user_dec_data = ""
    for index, user in enumerate(users, start=1):
        user_dec_data += f"👤 {index}. {user.get('fullname')}\n"
        user_buttons.append(
            InlineKeyboardButton(
                text=str(index),
                callback_data=f"User:{index}"
            )
        )
    return user_dec_data, user_buttons


fake_delete = InlineKeyboardButton(text="Remove Users that are absent", callback_data="fake_delete")
ask_delete_or_confirm = InlineKeyboardMarkup().add(fake_delete, confirm)


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
def p_and_j(callback_data):
    var = InlineKeyboardButton("Не смогу придти", callback_data=f"absence:{callback_data}")
    paid_and_joined_button = InlineKeyboardMarkup().add(var, go_back)
    return paid_and_joined_button
