# coding=utf-8
import asyncio
import os
from datetime import datetime

from aiogram.dispatcher import filters
from dotenv import load_dotenv
import pytz
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from sheet_delete import unix, delete_expired, delete, subtract_from_current_date
import buttons
import states
import database
from sheet_read import get_data_from_id, normalize_data, read_sheet_values
from sheet_write import write_registration
from sheet_update import update_registration

load_dotenv()

mess = """
⚠️⚠️⚠️

<b><b>Правила игры
Матчи проводятся по смешанным правилами футбола и мини-футбола, дополненными согласно настоящему положению:</b></b>



ℹ️ <b>1. Число игроков</b>


    • В случае травмы или отсутствия игрока, его может заменить любой другой игрок;
    
    • В составе команды на поле выходят количество команд в соответствии формату 5х5, 6х6, 7х7 или 8х8


    Минимум -1 человек от формата на поле от команды 
    4 при 5х5, 5 при 6х6 и т.д.


    • Количество замен, производимых командой во время матча, неограниченно. Разрешены обратные замены;

    • Вратарь может поменяться местами с любым игроком своей команды.

ℹ️ <b>2. Экипировка игроков</b>

    • Игрок не должен использовать такую экипировку или носить то, что представляет опасность для него самого или для другого игрока (включая ювелирные изделия любого вида);

    • Основной обязательной экипировкой игрока являются: манишка, футболка с рукавами, трусы, гетры, обувь (спортивная обувь с гладкой подошвой, либо бутсы-сороконжки);

    • Бутсы с шипами запрещены.


ℹ️ <b>3. Продолжительность игры</b>


    Игры на вылет:
	 <b>по 6 или 7 мин тайм</b>
    Игры 1 на 1: 
	<b>2 тайма по 26 минут</b>


    • Перерыв между таймами не должен превышать 5 минут

    • Контроль игрового времени осуществляется админом поля


ℹ️ <b>4. Решение спорных моментов</b>

Решение спорных моментов на поле осуществляется капитанами команд.


    • В случае пенальти во время матча, убедиться, что видео с нарушением было записано (если нет, то решение принятое на поле, остаётся финальным)

    • Тех пор идёт со счётом 3:0.


ℹ️ <b>5. Правила игры на поле</b>
Каждый игрок самостоятельно несёт отвественность за своё здоровье


    • Гол не может быть засчитан непосредственно с начального удара;

    • Положение «вне игры» не фиксируется;

    • Пенальти бьется с расстояния в 9 метров (ворота 5х2), 7 метров ворота (3х2);

    • Уход мяча за поле фиксируется в момент полного пересечения всего мяча линии. Пока его даже малая часть остаётся на линии - он в поле;

    • Вратарь вводит мяч в игру ударом по неподвижному мячу с поля из пределов штрафной площади. На ввод мяча вратарю дается 6 секунд;

    • Вратарь не может брать в руки пас от своего игрока, исключением является рикошет. Если всё же так случилось, то команда соперника пробивает свободный удар с линии штрафной;

    • Аут вводится ударом ноги по неподвижному мячу с боковой линии. Если мяч после ввода из аута попал в ворота, не коснувшись никого из игроков, то гол не засчитывается;

    • На ввод мяч из аута, со штрафного/свободного или углового удара команде дается 6 секунд. При этом игроки соперника должны располагаться не ближе 5 метров от мяча;

    • Игрокам запрещается использование подкатов в попытке сыграть в мяч, когда им играет или пытается сыграть соперник. За подкат без нарушения назначается свободный удар;

    • Не допускается преднамеренное воспрепятствие действиям вратаря (без мяча);

    • Нельзя вступать в контактную борьбу с вратарём (без мяча);

    • Запрещено удерживать мяч и играть лёжа;

    • Замена игрока запрещена через линию, вдоль которой стоят ворота.


ℹ️ <b>6. Особые случаи</b>

    • При возникновении ситуаций с выкриками с угрозой расправы, нанесения телесных травм или иной формулировкой, которая является угрозой жизни и здоровью игрока, будет выдаваться прямая дисквалификация от 2 до 10 матчей. Без возвращения средств;

    • При появлении побоев или нанесении телесных травм, в результате явной грубости, во время матча или на территории спортивных объектов до или после матча. Игрок может получить пожизненную дисквалификацию, а его команда техническое поражение в матче, в день которого это произошло. В плоть до снятия команды с турнира, в случае массовой драки и угроз. Без возвращения средств.

<i>Организаторы турнира оставляют за собой право решение спорных моментов не прописанных в правилах сообщества и не попадающим под правила футбола и мини-футбола.</i>

👤 Artiom Kiseliov
📅 31 марта, 19:32"""

# 🚫 ✅ ℹ️ ❓
token = os.getenv("TOKEN")
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
print("Bot started successfully")


@dp.message_handler(commands=["test"])
async def button_url(message: types.Message):
    await message.answer("somethin", reply_markup=buttons.btn)


def is_correct_text(text):
    return text not in ["Записаться на игру", "Моя команда"]


def is_registered(user: dict, tg_id: int):
    return any(str(u_id.get("id")) == str(tg_id) for u_id in user)


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
                reply_markup=buttons.per_or_three_button
            )
        else:
            await bot.send_message(callback_query.from_user.id, "🚫 вы уже присоединились к этой команде!")
    else:
        await bot.send_message(
            callback_query.from_user.id,
            text="🚫 Вы не можете играть в эту игру, потому что игра заполнена!"
        )


@dp.callback_query_handler(lambda c: c.data.startswith('only_me'))
async def only_me(callback: types.CallbackQuery):
    await bot.send_message(
        callback.from_user.id,
        "ℹ️ Ты выбрал вариант `только меня`. Пожалуйста, введите идентификатор вашей карты:"
    )
    await states.PaymentDetails.card_id.set()


@dp.message_handler(state=states.PaymentDetails.card_id)
async def get_card_id(message: types.Message, state: FSMContext):
    await state.update_data(card_id=message.text)
    await message.answer("❓ Введите карту CVV/CVC:")
    await states.PaymentDetails.CSV.set()


@dp.message_handler(state=states.PaymentDetails.CSV)
async def get_csv(message: types.Message, state: FSMContext):
    await state.update_data(CSV=message.text)
    await message.answer("❓ Введите срок действия карты:")
    await states.PaymentDetails.expire_date.set()


# --------------------------------------------------------------------------------------------------------- change team
# @dp.message_handler()
@dp.callback_query_handler(lambda c: c.data.startswith('change_team'))
async def change_team(callback: types.CallbackQuery, state: FSMContext):
    base = database.Model()
    keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    ras_keys = ["id", "date", "weekday", "address", "time", "max"]
    data = base.get(user_id=callback.from_user.id)
    if data is None:
        data = 0
    if data > 0:
        database.Model(user_id=int(callback.from_user.id), chance=int(data) + 1).update()
    match_id = (await state.get_data()).get("match_id")
    for index, some_data in enumerate(
            read_sheet_values(
                table_name="Матчи!A:J",
                keys=keys
            )
    ):
        if some_data.get("user_id") == str(callback.from_user.id) and some_data.get("match_id") == str(match_id):
            delete("Матчи", row_number=index + 2)

    data_values = read_sheet_values(table_name="Расписание!A1:G", keys=ras_keys)
    b_list = []
    dd = "\n\n"
    for index, text in enumerate(normalize_data(data_values)):
        b_list.append(
            buttons.InlineKeyboardButton(
                text=f"{index + 1}",
                callback_data=f"Example:{data_values[index]['id']}"
            )
        )
        get_discount()
        dd += f"✅ {index + 1}.  " + text + "\n\n"
    b = buttons.InlineKeyboardMarkup().add(*b_list)
    await bot.send_message(
        callback.from_user.id,
        text="ℹ️ Перед Вами ближайшие матчи.\nВы можете ознакомиться "
             "с более подробной информацией, такой как список участников и другое." + dd,
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
    regular_user = get_data_from_id(
        table_name="Матчи!A:G",
        id=str(message.from_user.id),
        keys=match_keys,
        key="user_id"
    )

    def is_regular():
        if not regular_user:
            return False
        for k in regular_user:
            if subtract_from_current_date(k.get("date")) > 15:
                return False
        return True

    money_to_pay = 0
    if int(state_data.get("amount_of_game")) == 1:
        if is_regular():
            money_to_pay = int(get_discount()[0].get("regular_user"))
        else:
            money_to_pay = int(get_discount()[0].get("new_user"))
    elif int(state_data.get("amount_of_game")) == 3:
        if is_regular():
            money_to_pay = int(get_discount()[0].get("regular_user")) * 3
        else:
            money_to_pay = int(get_discount()[0].get("new_user")) * 3
    # Here, you should implement the payment processing using the card details stored in the state.
    # And if the payment is successful, store the 3 bounces in the database.
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

    if user_exists():
        for index, i in enumerate(matches):
            if str(i.get("match_id")) == str(state_data.get("match_id")) and str(i.get("user_id")) == str(
                    message.from_user.id):
                update_registration(range_name="Матчи", sign="+", row_index=index + 2)
    else:
        write_registration("Матчи!A:G", list_of_values=final_data)

    await message.answer(str(money_to_pay))
    if database.Model().get_user(int(message.from_user.id)) is None:
        data = database.Model(
            user_id=int(message.from_user.id),
            chance=int(state_data.get("amount_of_game")) - 1
        )
        data.save()
    else:
        data = database.Model(
            user_id=int(message.from_user.id),
            chance=int(state_data.get("amount_of_game")) - 1
        )
        data.update()
    await message.answer("✅ Ваш платеж прошел успешно! Теперь вы можете присоединиться к любой команде")
    await message.answer(get_final_body_content(state_data.get("match_id")), reply_markup=buttons.change_team1)
    await state.finish()
    await state.update_data(match_id=state_data.get("match_id"))


@dp.message_handler(state=states.PaymentAmounts.amount_of_game)
@dp.callback_query_handler(lambda c: c.data.startswith('per'))
async def per_game(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(amount_of_game=1)
    await bot.send_message(
        callback.from_user.id,
        text="❓ Пожалуйста, введите идентификатор вашей карты:"
    )
    await states.PaymentDetails.card_id.set()


@dp.message_handler(state=states.PaymentAmounts.amount_of_game)
@dp.callback_query_handler(lambda c: c.data.startswith('three'))
async def three_games(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(amount_of_game=3)
    await bot.send_message(
        callback.from_user.id,
        text="❓ Пожалуйста, введите идентификатор вашей карты:"
    )
    await states.PaymentDetails.card_id.set()


@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    print(message.chat.id)
    user_id = read_sheet_values(table_name="Пользователи!B:B", keys=["id"])
    if is_registered(user_id, tg_id=message.from_user.id):
        await message.answer(
            f"👋👋👋 \nЗдравствуйте, {message.from_user.username}! Рад вас снова видеть. Вы можете записываться на игру "
            f"и принимать участие в футбольных турнирах.",
            reply_markup=buttons.two_buttons
        )
    else:
        await message.answer("👋👋👋 \nЗдравствуйте, для регистрации введите Фамилию и Имя (пример: Ордабаев Куралбек)")
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

    payed_users = ""
    for index, user in enumerate(data2, start=1):
        if user.get("pay") == "+":
            if unix(user.get("date"), user.get("time")) < 0:
                payed_users += f"{index}. {user.get('fullname')}\n"

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
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]

    def is_regular_user():
        match = get_data_from_id(
            table_name="Матчи!A:I",
            id=str(callback_query.from_user.id),
            keys=match_keys,
            key="user_id"
        )
        return len(match) > 0

    def is_joined_before():
        match = get_data_from_id(
            id=str(callback_query.from_user.id),
            table_name="Матчи!A:I",
            keys=match_keys,
            key="user_id"
        )
        if not match:
            return False
        for i in match:
            if i.get("match_id") == key_id:
                return True
        return False

    await state.update_data(match_id=int(key_id))

    if is_regular_user():
        base = database.Model()
        data = base.get(user_id=int(callback_query.from_user.id))
        is_payed = not ((data is None) or (int(data) == 0))
        if not is_joined_before():
            if is_payed:
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
        else:
            await bot.send_message(
                callback_query.from_user.id,
                get_final_body_content(key_id),
                reply_markup=buttons.change_team(key_id)
            )
    else:
        await bot.send_message(
            callback_query.from_user.id, mess, parse_mode="HTML", reply_markup=buttons.btn
        )


@dp.callback_query_handler(lambda c: c.data.startswith("rule"))
async def rules(callback_query: types.CallbackQuery, state: FSMContext):
    base = database.Model()
    key = await state.get_data()
    key_id = key.get("match_id")
    data = base.get(user_id=int(callback_query.from_user.id))
    is_payed = not ((data is None) or (int(data) == 0))
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]

    def is_joined_before():
        match = get_data_from_id(
            id=str(callback_query.from_user.id),
            table_name="Матчи!A:I",
            keys=match_keys,
            key="user_id"
        )
        if not match:
            return False
        for i in match:
            if i.get("match_id") == key_id:
                return True
        return False

    if is_joined_before():
        if is_payed:
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
    else:
        await bot.send_message(
            callback_query.from_user.id,
            get_final_body_content(key_id),
            reply_markup=buttons.change_team(key_id)
        )


# ------------------------------------------------------------------------------------------------ go back button
@dp.callback_query_handler(lambda c: c.data.startswith('go_back'))
async def go_back_button(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    ras_keys = ["id", "date", "weekday", "address", "time", "max"]
    data_values = read_sheet_values(table_name="Расписание!A1:G", keys=ras_keys)
    b_list = []
    dd = "\n\n"
    for index, text in enumerate(normalize_data(data_values)):
        b_list.append(
            buttons.InlineKeyboardButton(
                text=f"{index + 1}",
                callback_data=f"Example:{data_values[index]['id']}"
            )
        )
        dd += f"✅ {index + 1}.  " + text + "\n\n"
    b = buttons.InlineKeyboardMarkup().add(*b_list)
    await bot.send_message(
        callback_query.from_user.id,
        text="ℹ️ Перед Вами ближайшие матчи.\nВы можете ознакомиться "
             "с более подробной информацией, такой как список участников и другое." + dd,
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
        dd = "\n\n"
        for index, text in enumerate(normalize_data(data_values)):
            b_list.append(
                buttons.InlineKeyboardButton(
                    text=f"{index + 1}",
                    callback_data=f"Example:{data_values[index]['id']}"
                )
            )
            dd += f"✅ {index + 1}.  " + text + "\n\n"
        b = buttons.InlineKeyboardMarkup().add(*b_list)
        await message.answer(
            text="ℹ️ Перед Вами ближайшие матчи.\nВы можете ознакомиться "
                 "с более подробной информацией, такой как список участников и другое." + dd,
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
            await message.answer("ℹ️ Вы еще не присоединились ни к одной команде, давайте сделаем одну")
        for per_id in match_id_list:
            await message.answer(get_final_body_content(per_id), reply_markup=buttons.change_team(per_id))


# ------------------------------------------------------------------------------------------------ cancel button
@dp.callback_query_handler(lambda c: c.data.startswith('absence:'))
async def delete_absent_user(callback: types.CallbackQuery):
    ras_keys = ["id", "date", "weekday", "address", "time", "max"]
    keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone", "pay"]
    match_id = callback.data.split(":")[-1]
    user = read_sheet_values(table_name="Матчи!A1:I", keys=keys)
    for index, i in enumerate(user):
        if i.get("user_id") == str(callback.from_user.id) and i.get("match_id") == str(match_id):
            delete(sheet_name="Матчи", row_number=index + 2)
    await bot.send_message(callback.from_user.id, text="Выберите, где присоединиться", )
    data_values = read_sheet_values(table_name="Расписание!A1:G", keys=ras_keys)
    b_list = []

    dd = "\n\n"
    for index, text in enumerate(normalize_data(data_values)):
        b_list.append(
            buttons.InlineKeyboardButton(
                text=f"{index + 1}",
                callback_data=f"Example:{data_values[index]['id']}"
            )
        )
        dd += f"✅ {index + 1}.  " + text + "\n\n"
    b = buttons.InlineKeyboardMarkup().add(*b_list)
    await bot.send_message(
        callback.from_user.id,
        text="ℹ️ Перед Вами ближайшие матчи.\nВы можете ознакомиться "
             "с более подробной информацией, такой как список участников и другое." + dd,
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
        table_name="Пользователи!A:I",
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
    rem = list(user.values())
    final_data = list([dates.get("data"), dates.get("time"), dates.get("match_id")]) + rem + ["+"]
    match_keys = ["date", "time", "match_id", "user_id", "fullname", "username", "phone"]
    match = get_data_from_id(
        id=str(callback.from_user.id),
        keys=match_keys,
        table_name="Матчи!A:I",
        key="user_id"
    )

    def is_user_in():
        for m in match:
            if str(m.get("match_id")) == str(state_data.get("match_id")):
                return True
        return False

    if not is_user_in():
        write_registration(range_name="Матчи", list_of_values=final_data)
        await bot.send_message(callback.from_user.id, "Вы успешно присоединились к команде!")
    else:
        await bot.send_message(
            callback.from_user.id,
            text="Вы уже вступили в команду!"
        )
        ras_keys = ["id", "date", "weekday", "address", "time", "max"]
        data_values = read_sheet_values(table_name="Расписание!A1:G", keys=ras_keys)
        b_list = []

        dd = "\n\n"
        for index, text in enumerate(normalize_data(data_values)):
            b_list.append(
                buttons.InlineKeyboardButton(
                    text=f"{index + 1}",
                    callback_data=f"Example:{data_values[index]['id']}"
                )
            )
            dd += f"✅ {index + 1}.  " + text + "\n\n"
        b = buttons.InlineKeyboardMarkup().add(*b_list)
        await bot.send_message(
            callback.from_user.id,
            text="ℹ️ Перед Вами ближайшие матчи.\nВы можете ознакомиться "
                 "с более подробной информацией, такой как список участников и другое." + dd,
            reply_markup=b
        )


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
                await bot.send_message(chat_id=callback.from_user.id, text="количество игроков в команде полное")
        else:
            await bot.send_message(chat_id=callback.from_user.id, text="Вы уже вступили в команду!")
        await bot.send_message(
            chat_id=callback.from_user.id,
            text=get_final_body_content(match_id),
            reply_markup=buttons.change_team(match_id)
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
