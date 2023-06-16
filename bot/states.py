from aiogram.dispatcher.filters.state import State, StatesGroup


class UserDetails(StatesGroup):
    full_name = State()
    phone_number = State()
    region = State()
    match_id = State()
# moy kommand
#