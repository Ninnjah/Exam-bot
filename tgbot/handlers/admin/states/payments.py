from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminPayments(StatesGroup):
    payment = State()
    confirm = State()
