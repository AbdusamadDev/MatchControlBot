import asyncio
import logging
import os
# import time
from datetime import datetime

from dotenv import load_dotenv
import pytz
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from sheet_delete import unix, delete_expired, delete, subtract_from_current_date
from bot import buttons, states, database
from sheet_read import get_data_from_id, normalize_data, read_sheet_values
from sheet_write import write_registration
from sheet_update import update_registration

logging.basicConfig(level=logging.INFO)
load_dotenv()

# Load environment variables
token = os.getenv("TOKEN")
bot = Bot(token=token)

# Initialize bot and dispatcher
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def is_correct_text(text):
    return text not in ["Записаться на игру", "Моя команда"]


def is_registered(user: dict, tg_id: int):
    return any(str(id.get("id")) == str(tg_id) for id in user)


# ------------------------------------------------------------------------------------------------ Oplatit igru button
@dp.callback_query_handler(lambda c: c.data.startswith('pay_game'))
async def pay_game(callback_query: types.CallbackQuery, state: FSMContext):
    match_id = (await state.get_data()).get("match_id")
    await callback_query.message.delete()
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    date_keys = ["match_id", "data", "address", "date", "time", "max"]
    dates = get_data_from_id(
        table_name="Расписание!A1:G",
        id=str(match_id),
        keys=date_keys,
        key="match_id"
    )[0]
    matches = get_data_from_id(
        id=str(match_id),
        table_name="Матчи!A:G",
        keys=match_keys,
        key="match_id"
    )
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    # print("Max player: ", int(dates.get("max")))
    # print("Match ID: ", match_id)
    # print("len matches ", len(matches))
    if int(dates.get("max")) > len(matches):

        team_user = get_data_from_id(
            id=str(callback_query.from_user.id),
            table_name="Матчи!A:I",
            keys=match_keys,
            key="user_id"
        )

        def is_payed():
            return any(str(k.get("match_id")) == str(match_id) and k.get("pay") == "+" for k in team_user)

        if not is_payed():
            await bot.send_message(
                callback_query.from_user.id,
                text="Выбор формата оплаты",
                reply_markup=buttons.per_or_team_button
            )
        else:
            await bot.send_message(callback_query.from_user.id, "Вы уже заплатили за игру")
    else:
        await bot.send_message(callback_query.from_user.id, text="You cannot play in this game because game is full!")


@dp.callback_query_handler(lambda c: c.data.startswith('only_me'))
async def only_me(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(team_or_one="me")
    await bot.send_message(callback.from_user.id, "You selected only me. Please enter your Card ID:")
    await states.PaymentDetails.card_id.set()
    # print("State data: ", await state.get_data())


@dp.message_handler(state=states.PaymentAmounts.team_or_one)
@dp.callback_query_handler(lambda c: c.data.startswith('for_team'))
async def for_team(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(team_or_one="team")
    await bot.send_message(callback.from_user.id, "You selected for team. Please enter your Card ID:")
    await states.PaymentDetails.card_id.set()
    # print("State data: ", await state.get_data())


@dp.message_handler(state=states.PaymentDetails.card_id)
async def get_card_id(message: types.Message, state: FSMContext):
    await state.update_data(card_id=message.text)
    await message.answer("Card CVV/CVC")
    await states.PaymentDetails.CSV.set()
    # print("State data: ", await state.get_data())


@dp.message_handler(state=states.PaymentDetails.CSV)
async def get_csv(message: types.Message, state: FSMContext):
    await state.update_data(CSV=message.text)
    await message.answer("Card Expire date:")
    await states.PaymentDetails.expire_date.set()
    # print("State data: ", await state.get_data())


# --------------------------------------------------------------------------------------------------------- change team
# @dp.message_handler()
@dp.callback_query_handler(lambda c: c.data.startswith('change_team'))
async def change_team(callback: types.CallbackQuery, state: FSMContext):
    # Добавляем обновленные данные состояния, если необходимо
    # await state.update_data(match_id=int(key_id))
    base = database.Model()
    keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    key = await state.get_data()
    data = base.get(user_id=callback.from_user.id)
    # if data is not None:
    database.Model(user_id=int(callback.from_user.id), chance=int(data) + 1).update()
    data_values = read_sheet_values(
        table_name="Расписание!A1:G",
        keys=["match_id", "date", "weekday", "address", "time", "max"]
    )
    match_id = (await state.get_data()).get("match_id")
    # print("Match ID: ", match_id)
    for index, some_data in enumerate(
            read_sheet_values(
                table_name="Матчи!A:J",
                keys=keys
            )
    ):
        # print(some_data)
        if some_data.get("user_id") == str(callback.from_user.id) and some_data.get("match_id") == str(match_id):
            # print("Mother hackin is ready to go")
            # print("This is index: ", index)
            delete("Матчи", row_number=index + 2)
    b_list = []

    for index, text in enumerate(normalize_data(data_values)):
        b_list.append(
            buttons.InlineKeyboardButton(
                text=f"{index + 1}. {text}",
                callback_data=f"Example:{data_values[index]['match_id']}"
            )
        )
    b = buttons.InlineKeyboardMarkup(row_width=1).add(*b_list)
    await bot.send_message(
        callback.from_user.id,
        text="Перед Вами ближайшие матчи.\nВы можете ознакомиться "
             "с более подробной информацией, такой как список участников и другое.",
        reply_markup=b
    )


def get_discount():
    keys = ["regular_user", "new_user", "triple_games"]
    discounts = read_sheet_values(table_name="Цены", keys=keys)
    return discounts


# -------------------------------------------------------------------------------------------------------
@dp.message_handler(state=states.PaymentDetails.expire_date)
async def get_expiry(message: types.Message, state: FSMContext):
    await state.update_data(expire_date=message.text)
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    state_data = await state.get_data()
    money_to_pay = 0
    regular_user = get_data_from_id(
        table_name="Матчи!A:G",
        id=str(message.from_user.id),
        keys=match_keys,
        key="user_id"
    )

    def is_regular():
        for k in regular_user:
            if subtract_from_current_date(k.get("date")) > 15:
                return False
        return True

    # print(is_regular())
    # print(get_discount())
    if int(state_data.get("amount_of_game")) == 3:
        money_to_pay = int(get_discount()[0].get("triple_games")) * 3
    elif is_regular():
        money_to_pay = int(get_discount()[0].get("regular_user"))
    else:
        money_to_pay = int(get_discount()[0].get("new_user"))
    # Here, you should implement the payment processing using the card details stored in the state.
    # And if the payment is successful, store the 3 bounces in the database.
    # date_keys = ["match_id", "data", "address", "date", "time", "max"]
    user = get_data_from_id(
        id=str(message.from_user.id),
        table_name="Пользователи!A:G",
        keys=["date", "user_id", "fullname", "username", "phone", "region"],
        key="user_id"
    )[0]
    del user["region"], user["date"]
    matches = read_sheet_values(
        table_name="Матчи!A:G",
        keys=match_keys,
    )
    date_keys = ["match_id", "data", "address", "date", "time", "max"]
    dates = get_data_from_id(
        table_name="Расписание!A1:G",
        id=str(state_data.get("match_id")),
        keys=date_keys,
        key="match_id"
    )[0]
    user = get_data_from_id(
        id=str(message.from_user.id),
        table_name="Пользователи!A:G",
        keys=["date", "user_id", "fullname", "username", "phone", "region"],
        key="user_id"
    )[0]
    del user["region"], user["date"]
    rem = list(user.values())
    final_data = list([dates.get("data"), dates.get("time"), dates.get("match_id")]) + rem + ["+"]

    def user_exists():
        for j in matches:
            if j.get("user_id") == str(message.from_user.id) and j.get("match_id") == str(state_data.get("match_id")):
                return True

    # print(user_exists())
    if user_exists():
        for index, i in enumerate(matches):
            if str(i.get("match_id")) == str(state_data.get("match_id")) and str(i.get("user_id")) == str(
                    message.from_user.id):
                # print("Condition worked")
                update_registration(range_name="Матчи", sign="+", row_index=index + 2)
    else:
        # print(">>> ", final_data)
        write_registration("Матчи!A:G", list_of_values=final_data)
    if state_data.get("team_or_one") == "team":
        players_count = get_data_from_id(
            id=str(state_data.get("match_id")),
            table_name="Матчи!A:I",
            keys=match_keys,
            key="match_id"
        )
        # print(len(players_count))
        # print(players_count)
        team_max = get_data_from_id(
            id=str(state_data.get("match_id")),
            table_name="Расписание!A:G",
            keys=date_keys,
            key="match_id"
        )[0].get("max")
        # print(state_data.get("match_id"))
        # print("Team Max ", team_max)

        if int(state_data.get("amount_of_game")) == 1:
            money_to_pay += (2500 * ((int(team_max) - len(players_count)) + 1))
        else:
            money_to_pay += 3 * (2500 * ((int(team_max) - len(players_count)) + 1))
    elif state_data.get("team_or_one") == "me":
        if int(state_data.get("amount_of_game")) == 1:
            money_to_pay += 2500
        else:
            money_to_pay += 3 * 2500
    # print("Amount of money: ", money_to_pay)
    # print(database.Model().get_user(int(message.from_user.id)))
    if database.Model().get_user(int(message.from_user.id)) is None:
        print("Data is None")
        data = database.Model(
            user_id=int(message.from_user.id),
            chance=int(state_data.get("amount_of_game")) - 1
        )
        data.save()
    else:
        # print(state_data)
        data = database.Model(
            user_id=int(message.from_user.id),
            chance=int(state_data.get("amount_of_game")) - 1
        )
        data.update()
    await message.answer("Your payment is successful!")
    await message.answer(get_final_body_content(state_data.get("match_id")), reply_markup=buttons.change_team1)
    await state.finish()
    await state.update_data(match_id=state_data.get("match_id"))


@dp.message_handler(state=states.PaymentAmounts.amount_of_game)
@dp.callback_query_handler(lambda c: c.data.startswith('per'))
async def per_game(callback: types.CallbackQuery, state: FSMContext):
    amount = 2500
    await state.update_data(amount_of_game=1)
    await bot.send_message(
        callback.from_user.id,
        text="2500 from you. Please choose how many games you want?",
        reply_markup=buttons.who_button
    )


@dp.message_handler(state=states.PaymentAmounts.amount_of_game)
@dp.callback_query_handler(lambda c: c.data.startswith('three'))
async def three_games(callback: types.CallbackQuery, state: FSMContext):
    amount = 5100
    await state.update_data(amount_of_game=3)
    await bot.send_message(
        callback.from_user.id,
        text="5100 from you. Please choose how many games you want?",
        reply_markup=buttons.who_button
    )


# ------------------------------------------------------------------------------------------------ Starting the bot
@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    user_id = read_sheet_values(table_name="Пользователи!B:B", keys=["id"])
    if is_registered(user_id, tg_id=message.from_user.id):
        await message.answer(
            f"Здравствуйте, {message.from_user.username}! Рад вас снова видеть. Вы можете записываться на игру "
            f"и принимать участие в футбольных турнирах.",
            reply_markup=buttons.two_buttons
        )
    else:
        await message.answer("Здравствуйте, для регистрации введите Фамилию и Имя (пример: Ордабаев Куралбек)")
        await states.UserDetails.full_name.set()


@dp.message_handler(state=states.UserDetails.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("Нажатие кнопки не допускается")
    else:
        full_name = message.text
        await state.update_data(full_name=full_name)
        await message.answer("Введите свой номер телефона в формате +7721234567")
        await states.UserDetails.phone_number.set()


@dp.message_handler(state=states.UserDetails.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("Нажатие кнопки не допускается")
    else:
        phone_number = message.text
        if len(phone_number) < 10:
            await message.answer("Неправильный номер, повторите попытку.")
        else:
            # if not str(phone_number).isdigit():
            #    await message.answer("Enter valid phone number")
            # else:
            await state.update_data(phone_number=phone_number)
            await message.answer("Введите свой город (пример: Астана)")
            await states.UserDetails.region.set()


# ------------------------------------------------------------------------------------------- Add user to registration
@dp.message_handler(state=states.UserDetails.region)
async def process_region(message: types.Message, state: FSMContext):
    if not is_correct_text(message.text):
        await message.answer("Нажатие кнопки не допускается")
    else:
        region = message.text
        await state.update_data(region=region)
        user_data = await state.get_data()
        full_name = user_data.get("full_name")
        phone_number = user_data.get("phone_number")
        region = user_data.get("region")
        username = message.from_user.username
        user_id = message.from_user.id
        if "+" not in phone_number:
            phone_number = "+" + phone_number
        date = datetime.now(pytz.timezone("Asia/Almaty")).strftime("%d.%m.%Y")
        ls = [date, user_id, full_name, f"https://t.me/{username}", phone_number, region]
        write_registration("Пользователи!A:E", ls)
        await message.answer(
            text="Спасибо за регистрацию в “Газон”! Теперь вы можете записываться на игру "
                 "и принимать участие в футбольных турнирах.",
            reply_markup=buttons.two_buttons
        )

        await state.finish()


# ------------------------------------------------------------------------------------------------ Normalize text
def get_final_body_content(key_id):
    keys = ["id", "date", "weekday", "address", "time"]
    data1 = get_data_from_id(id=str(key_id), table_name="Расписание!A1:G", keys=keys, key="id")
    date_address = normalize_data(data1)[0] + "\n\n"

    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    data2 = get_data_from_id(id=str(key_id), table_name="Матчи!A1:I", keys=match_keys, key="match_id")
    # print(data2)

    payed_users = ""
    for index, user in enumerate(data2, start=1):
        if user.get("pay") == "+":
            if unix(user.get("date"), user.get("time")) < 0:
                payed_users += f"{index}. {user.get('fullname')}\n"  # Извлекаем значения из списка

    reserve_users = '\n'.join(
        [f"{index}. {user.get('fullname')}" for index, user in enumerate(data2, start=1) if
         user.get("pay") != "+"])
    payload = f"Команда:\n{payed_users}\n\nРезерв:\n{reserve_users}"
    return date_address + payload


# ------------------------------------------------------------------------------------------------ prosmotret button
@dp.callback_query_handler(lambda c: c.data.startswith('Example:'))
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    data_parts = callback_query.data.split(':')
    key_id = data_parts[-1]

    # Добавляем обновленные данные состояния, если необходимо
    await state.update_data(match_id=int(key_id))
    base = database.Model()
    data = base.get(user_id=int(callback_query.from_user.id))
    is_payed = not ((data is None) or (int(data) == 0))
    # print(data, is_payed)
    # Отправляем новое сообщение с обновленной информацией
    if is_payed:
        # print("Is payed equals to True")
        await bot.send_message(
            callback_query.from_user.id,
            get_final_body_content(key_id),
            reply_markup=buttons.payed_button
        )
    else:
        await bot.send_message(
            callback_query.from_user.id,
            get_final_body_content(key_id),
            reply_markup=buttons.register_buttons
        )


# ------------------------------------------------------------------------------------------------ go back button
@dp.callback_query_handler(lambda c: c.data.startswith('go_back'))
async def go_back_button(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    keys = ["id", "date", "weekday", "address", "time"]
    data_values = read_sheet_values(table_name="Расписание!A1:G", keys=keys)
    b_list = []

    for index, text in enumerate(normalize_data(data_values)):
        b_list.append(
            buttons.InlineKeyboardButton(
                text=f"{index + 1}. {text}\n",
                callback_data=f"Example:{data_values[index]['id']}"
            )
        )
    b = buttons.InlineKeyboardMarkup(row_width=1).add(*b_list)
    await bot.send_message(
        callback_query.from_user.id,
        text="Перед Вами ближайшие матчи.\nВы можете ознакомиться "
             "с более подробной информацией, такой как список участников и другое.",
        reply_markup=b
    )


# ------------------------------------------------------------------------------------------------ keyboard buttons
@dp.message_handler()
async def basic_message(message: types.Message):
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    keys = ["id", "date", "weekday", "address", "time", "max"]
    delete_expired(table="Расписание!A1:G", keys=keys)
    if message.text == "Записаться на игру":

        data_values = read_sheet_values(table_name="Расписание!A1:G", keys=keys)
        b_list = []

        for index, text in enumerate(normalize_data(data_values)):
            b_list.append(
                buttons.InlineKeyboardButton(
                    text=f"{index + 1}. {text}",
                    callback_data=f"Example:{data_values[index]['id']}"
                )
            )
        b = buttons.InlineKeyboardMarkup(row_width=1).add(*b_list)
        await message.answer(
            text="Перед Вами ближайшие матчи.\nВы можете ознакомиться "
                 "с более подробной информацией, такой как список участников и другое.",
            reply_markup=b
        )
    elif message.text == "Моя команда":
        team_user = get_data_from_id(
            id=str(message.from_user.id),
            table_name="Матчи!A:I",
            keys=match_keys,
            key="user_id"
        )
        match_id_list = []
        for i in team_user:
            match_id_list.append(i.get("match_id"))

        if not match_id_list:
            await message.answer("Вы еще не присоединились ни к одной команде, давайте сделаем одну")
        for per_id in match_id_list:
            try:
                await message.answer(get_final_body_content(per_id), reply_markup=buttons.absence(per_id))
            except Exception:
                print(match_id_list)


# ------------------------------------------------------------------------------------------------ cancel button
@dp.callback_query_handler(lambda c: c.data.startswith('absence:'))
async def delete_absent_user(callback: types.CallbackQuery):
    ras_keys = ["id", "date", "weekday", "address", "time", "max"]
    keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    match_id = callback.data.split(":")[-1]
    user = read_sheet_values(table_name="Матчи!A1:I", keys=keys)
    # print(user, match_id)
    for index, i in enumerate(user):
        # print(i.get("user_id"), i.get("match_id"))
        if i.get("user_id") == str(callback.from_user.id) and i.get("match_id") == str(match_id):
            # print("-----------------------------------------------------")
            print(delete(sheet_name="Матчи", row_number=index + 2))
    await bot.send_message(callback.from_user.id, text="Choose where to join", )
    data_values = read_sheet_values(table_name="Расписание!A1:G", keys=ras_keys)
    b_list = []

    for index, text in enumerate(normalize_data(data_values)):
        b_list.append(
            buttons.InlineKeyboardButton(
                text=f"{index + 1}. {text}",
                callback_data=f"Example:{data_values[index]['id']}"
            )
        )
    b = buttons.InlineKeyboardMarkup(row_width=1).add(*b_list)
    chance = database.Model().get(int(callback.from_user.id))
    database.Model(user_id=int(callback.from_user.id), chance=int(chance + 1)).update()
    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Перед Вами ближайшие матчи.\nВы можете ознакомиться "
             "с более подробной информацией, такой как список участников и другое.",
        reply_markup=b
    )


# ------------------------------------------------------------------------------------------------ Play button

@dp.callback_query_handler(lambda c: c.data == 'play')
async def play(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    chance = database.Model().get(user_id=int(callback.from_user.id))
    database.Model(chance=int(chance) - 1, user_id=int(callback.from_user.id)).update()
    state_data = await state.get_data()
    # Here, you should implement the payment processing using the card details stored in the state.
    # And if the payment is successful, store the 3 bounces in the database.
    user = get_data_from_id(
        id=str(callback.from_user.id),
        table_name="Пользователи!A:G",
        keys=["date", "user_id", "fullname", "username", "phone", "region"],
        key="user_id"
    )[0]
    del user["region"], user["date"]
    date_keys = ["match_id", "data", "address", "date", "time", "max"]
    dates = get_data_from_id(
        table_name="Расписание!A1:G",
        id=str(state_data.get("match_id")),
        keys=date_keys,
        key="match_id"
    )[0]
    user = get_data_from_id(
        id=str(callback.from_user.id),
        table_name="Пользователи!A:G",
        keys=["date", "user_id", "fullname", "username", "phone", "region"],
        key="user_id"
    )[0]
    del user["region"], user["date"]
    rem = list(user.values())
    final_data = list([dates.get("data"), dates.get("time"), dates.get("match_id")]) + rem + ["+"]
    write_registration(range_name="Матчи", list_of_values=final_data)
    await bot.send_message(callback.from_user.id, "Your balance decreased")


# ------------------------------------------------------------------------------------------------ Xochu igrat button
@dp.callback_query_handler(lambda c: c.data == 'play_button')
async def message1(callback: types.CallbackQuery, state: FSMContext):
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    match_state = await state.get_data()
    match_id = match_state.get("match_id")
    matches = get_data_from_id(
        id=str(match_id),
        table_name="Матчи!A:G",
        keys=match_keys,
        key="match_id"
    )

    try:
        date_keys = ["match_id", "data", "address", "date", "time", "max"]
        dates = get_data_from_id(
            table_name="Расписание!A1:G",
            id=str(match_id),
            keys=date_keys,
            key="match_id"
        )[0]
        user = get_data_from_id(
            id=str(callback.from_user.id),
            table_name="Пользователи!A:G",
            keys=["date", "user_id", "fullname", "username", "phone", "region"],
            key="user_id"
        )[0]
        del user["region"], user["date"]
        rem = list(user.values())
        final_data = list([dates.get("data"), dates.get("time"), dates.get("match_id")]) + rem

        def is_joined():
            for i in matches:
                # print(i)
                if i.get("user_id") == str(callback.from_user.id):
                    return True

            return False

        if not is_joined():
            if int(dates.get("max")) > len(matches):
                write_registration(
                    range_name="Матчи!A:G",
                    list_of_values=final_data
                )
                await bot.send_chat_action(callback.from_user.id, "typing")
                await asyncio.sleep(2)
                await bot.send_message(chat_id=callback.from_user.id, text="Вы успешно записались на игру!")
            else:
                await bot.send_message(chat_id=callback.from_user.id, text="Max player exceeded")
        else:
            await bot.send_message(chat_id=callback.from_user.id, text="Вы уже вступили в команду!")
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=get_final_body_content(match_id),
            reply_markup=buttons.change_team
        )
    except IndexError as error:
        await bot.send_chat_action(callback.from_user.id, "typing")
        await asyncio.sleep(2)
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=f"Error Body: {str(error)}"
        )

    await bot.delete_message(callback.from_user.id, callback.message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)