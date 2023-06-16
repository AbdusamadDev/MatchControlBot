import asyncio
import logging
import os
from datetime import datetime

import pytz
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from dotenv import load_dotenv

from bot import buttons, states
from sheet_read import get_data_from_id, normalize_data, read_sheet_values
from sheet_write import write_registration

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
token = os.getenv("TOKEN")

# Initialize bot and dispatcher
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


def is_registered(user: dict, tg_id: int):
    return any(str(id.get("id")) == str(tg_id) for id in user)


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
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer("Введите свой номер телефона в формате +7721234567")
    await states.UserDetails.phone_number.set()


@dp.message_handler(state=states.UserDetails.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    phone_number = message.text
    if len(phone_number) < 10:
        await message.answer("Неправильный номер, повторите попытку.")
    else:
        await state.update_data(phone_number=phone_number)
        await message.answer("Введите свой город (пример: Астана)")
        await states.UserDetails.region.set()


@dp.message_handler(state=states.UserDetails.region)
async def process_region(message: types.Message, state: FSMContext):
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
    date = datetime.now(pytz.timezone("Asia/Almaty")).strftime("%Y-%m-%d %H:%M")
    ls = [date, user_id, full_name, f"https://t.me/{username}", phone_number, region]
    write_registration("Пользователи!A:E", ls)
    await message.answer(
        text="Спасибо за регистрацию в “Газон”! Теперь вы можете записываться на игру "
             "и принимать участие в футбольных турнирах.",
        reply_markup=buttons.two_buttons
    )

    await state.finish()


def get_final_body_content(key_id):
    keys = ["id", "date", "weekday", "address", "time"]
    data1 = get_data_from_id(id=str(key_id), table_name="Расписание!A1:G", keys=keys, key="id")
    date_address = normalize_data(data1)[0] + "\n\n"

    match_keys = ["date", "time", "match_id", "team", "user_id", "fullname", "username", "phone", "pay"]
    data2 = get_data_from_id(id=str(key_id), table_name="Матчи!A1:G", keys=match_keys, key="match_id")

    payed_users = '\n'.join(
        [f"{index}. {user.get('fullname')}" for index, user in enumerate(data2, start=1) if user.get("pay") == "+"])
    reserve_users = '\n'.join(
        [f"{index}. {user.get('fullname')}" for index, user in enumerate(data2, start=1) if user.get("pay") != "+"])

    payload = f"Команда:\n{payed_users}\n\nReserve:\n{reserve_users}"
    return date_address + payload


@dp.callback_query_handler(lambda c: c.data.startswith('Example:'))
async def process_callback_button(callback_query: types.CallbackQuery, state: FSMContext):
    data_parts = callback_query.data.split(':')
    key_id = data_parts[-1]
    await state.update_data(match_id=int(key_id))
    await bot.send_message(
        callback_query.from_user.id,
        get_final_body_content(key_id),
        reply_markup=buttons.register_buttons
    )


@dp.callback_query_handler(lambda c: c.data.startswith('go_back'))
async def go_back_button(callback_query: types.CallbackQuery):
    keys = ["id", "date", "weekday", "address", "time"]
    data_values = read_sheet_values(table_name="Расписание!A1:G", keys=keys)
    for index, text in enumerate(normalize_data(data_values)):
        await bot.send_message(
            callback_query.from_user.id,
            text=text,
            reply_markup=buttons.InlineKeyboardMarkup().add(
                buttons.InlineKeyboardButton(
                    text="Просмотреть",
                    callback_data=f"Example:{data_values[index]['id']}"
                )
            )
        )


@dp.message_handler()
async def basic_message(message: types.Message, state: FSMContext):
    if message.text == "Записаться на игру":
        await message.answer(
            text="Перед Вами ближайшие матчи. Вы можете ознакомиться "
                 "с более подробной информацией, такой как список участников и другое.")
        keys = ["id", "date", "weekday", "address", "time"]
        data_values = read_sheet_values(table_name="Расписание!A1:G", keys=keys)
        for index, text in enumerate(normalize_data(data_values)):
            await message.answer(
                text=text,
                reply_markup=buttons.InlineKeyboardMarkup().add(
                    buttons.InlineKeyboardButton(
                        text="Посмотреть",
                        callback_data=f"Example:{data_values[index]['id']}"
                    )
                )
            )
    elif message.text == "Моя команда":
        match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
        keys = ["id", "date", "weekday", "address", "time"]
        match_id_value = await state.get_data()
        team = get_data_from_id(
            id=str(match_id_value.get("match_id")),
            table_name="Матчи!A:G",
            keys=match_keys,
            key="match_id"
        )
        if team:
            await message.answer(text=normalize_data(team)[0])
        else:
            await message.answer("Вы еще не присоединились к команде. Давайте присоединимся!")
    else:
        await message.answer("Сообщение не распознано!")


@dp.callback_query_handler(lambda c: c.data.startswith('play_button'))
async def message(callback: types.CallbackQuery, state: FSMContext):
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    match_state = await state.get_data()
    match_id = match_state.get("match_id")
    matches = get_data_from_id(
        id=str(match_id),
        table_name="Матчи!A:G",
        keys=match_keys,
        key="match_id"
    )

    def is_joined_to_match():
        if not matches:
            return False
        for match in matches:
            if str(callback.from_user.id) in match.values():
                return True
        return False

    if is_joined_to_match():
        await bot.send_chat_action(callback.from_user.id, "typing")
        await asyncio.sleep(2)
        await bot.send_message(chat_id=callback.from_user.id, text="Вы уже участвуете в игре!")
    else:
        try:
            date_keys = ["match_id", "data", "address", "date", "time"]
            dates = get_data_from_id(
                table_name="Расписание!A1:F",
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
            final_data = list([dates.get("data"), dates.get("time"), dates.get("match_id")]) + list(user.values())
            write_registration(
                range_name="Матчи!A:G",
                list_of_values=final_data
            )
            await bot.send_chat_action(callback.from_user.id, "typing")
            await asyncio.sleep(2)
            await bot.send_message(chat_id=callback.from_user.id, text="Вы успешно записались на игру!")
        except IndexError:
            await bot.send_chat_action(callback.from_user.id, "typing")
            await asyncio.sleep(2)
            await bot.send_message(
                chat_id=callback.from_user.id,
                text="Произошла ошибка при записи на игру, попробуйте еще раз!"
            )

    await bot.delete_message(callback.from_user.id, callback.message.message_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

# After successful team registration, all details should be shown
# username => fullname, with link that delivers to that user chat
# payed and not payed users should be shown seperate as reserve users, payed users
# if not registered before, privacy and policy terms of game should be shown, and if registered, shouldn't be shown
