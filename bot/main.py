from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
import pytz, sqlite3, os, logging

from sheet_write import write_registration
from sheet_read import read_sheet_values, normalize_data, get_data_from_id
from bot import buttons, states

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
    print(user_id)
    if is_registered(user_id, tg_id=message.from_user.id):
        await message.answer(
            f"Здравствйте {message.from_user.username}, Рад вас снова видеть. Вы можете "
            f"записываться на игру и принимать участие в футбольных турнирах",
            reply_markup=buttons.two_buttons)

    else:
        await message.answer("Здравствуйте, для регистрации введите Фамилия и Имя (пример: Ордабаев Куралбек)")
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
    date = str(datetime.now(pytz.timezone("Asia/Almaty"))).split(":")
    combined = date[0] + ":" + date[1]
    days = combined.split()[0]
    hours = combined.split()[-1]
    days_hours = days + "   " + hours
    ls = [days_hours, user_id, full_name, "https://t.me/" + str(username), phone_number, region]
    write_registration("Пользователи!A:E", ls)
    await message.answer(
        text="Спасибо за регистрацию в “Газон” Теперь вы можете записываться на игру "
             "и принимать участие в футбольных турнирах",
        reply_markup=buttons.two_buttons
    )

    # await state.finish()


def get_final_body_content(key_id):
    keys = ["id", "date", "weekday", "address", "time"]
    data1 = get_data_from_id(id=key_id, table_name="Расписание!A1:G", keys=keys, key="id")
    date_address = normalize_data(data1)[0] + "\n\n"

    match_keys = ["match_id", "team", "user_id", "fullname", "username", "phone", "pay"]
    data2 = get_data_from_id(id=key_id, table_name="Матчи!A1:G", keys=match_keys, key="match_id")

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
async def basic_message(message: types.Message):
    if message.text == "Записаться на игру":
        await message.answer(
            text="Перед Вами ближайшие матчи, можете ознакомиться "
                 "с более подробной информацией (список участников и др)")
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
        match_keys = ["match_id", "team", "user_id", "fullname", "username", "phone", "pay"]
        keys = ["id", "date", "weekday", "address", "time"]
        try:
            match_id = get_data_from_id(
                id=str(message.from_user.id),
                table_name="Матчи!A:G",
                keys=match_keys,
                key="user_id"
            )[0].get("match_id")
            team = get_data_from_id(
                id=match_id,
                table_name="Расписание!A:G",
                keys=keys,
                key="id"
            )
            await message.answer(text=normalize_data(team)[0])
        except IndexError:
            await message.answer("You have not joined any team yet, let's join one!")
    else:
        await message.answer("Message isn't recognized!")


@dp.callback_query_handler(lambda c: c.data.startswith('play_button'))
async def message(callback: types.CallbackQuery, state: FSMContext):
    match_keys = ["match_id", "team", "user_id", "fullname", "username", "phone", "pay"]
    match_state = await state.get_data()
    match_id = match_state.get("match_id")
    print(match_id)
    matches = get_data_from_id(
        id=match_id,
        table_name="Матчи!A:G",
        keys=match_keys,
        key="match_id"
    )
    print(matches)

    def is_joined_to_match():
        if not matches:
            return False
        for match in matches:
            if str(callback.from_user.id) in match.values():
                return True
        return False

    if is_joined_to_match():
        await bot.send_message(chat_id=callback.from_user.id, text="You have already in match!")
    else:
        user = get_data_from_id(
            id=str(callback.from_user.id),
            table_name="Пользователи!A:G",
            keys=["date", "user_id", "fullname", "username", "phone", "region"],
            key="user_id"
        )[0]
        del user["region"], user["date"]
        write_registration(
            range_name="Матчи!A:G",
            list_of_values=[1] + list(user.values())  # Will be updated to match id or something
        )
        await bot.send_message(
            chat_id=callback.from_user.id,
            text="You are added to team as a reserve player\nJust after payment you will be offered to a game"

        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
