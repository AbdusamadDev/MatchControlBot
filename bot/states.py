from aiogram.dispatcher.filters.state import State, StatesGroup


class UserDetails(StatesGroup):
    full_name = State()
    phone_number = State()
    region = State()
    match_id = State()


class PaymentDetails(StatesGroup):
    card_id = State()
    CSV = State()
    expire_date = State()


class PaymentAmounts(StatesGroup):
    amount_of_game = State()
    # team_or_one = State()
