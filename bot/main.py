import logging
import os
from datetime import datetime
from dotenv import load_dotenv
import pytz
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from sheet_write import write_registration
from sheet_read import read_sheet_values, normalize_data
from auth import get_credentials
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


@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
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
        text="Перед Вами ближайшие матчи, можете ознакомиться с более подробной информацией (список участников и др)")
    data_values = read_sheet_values(get_credentials())
    for index, text in enumerate(normalize_data(data_values)):
        await message.answer(
            text=text,
            reply_markup=buttons.InlineKeyboardMarkup().add(
                buttons.InlineKeyboardButton(text="Подробнее", callback_data=f"Example:{data_values[index]['id']}")
            )
        )
    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith('Example:'))
async def process_callback_button(callback_query: types.CallbackQuery):
    data_parts = callback_query.data.split(':')
    if len(data_parts) == 2:
        key_id = data_parts[1]
        await bot.send_message(callback_query.from_user.id, f"ID ключа: {key_id}")
        await callback_query.answer('Кнопка нажата')
    else:
        await callback_query.answer('Ошибка обработки данных')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
