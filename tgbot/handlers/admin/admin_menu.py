from aiogram import Dispatcher
from aiogram.types import Message

from tgbot.middlewares.locale import _
from tgbot.models.role import UserRole
from tgbot.services.repository import Repo


async def admin_start(m: Message):
    await m.answer(_(
        "Привет, Админ! Вот команды для тебя:\n"
        "/users - список всех пользователей\n"
        "/users_graph - график динамики пользователей\n"
        "/ticket_stats - список всех решенных билетов\n"
        "/ticket_csv - таблица всех решенных билетов\n"
        "/ticket_plot - график всех решенных билетов\n"
        "/users_top - график топа пользователей\n"
        "/set_payment - задать ссылку для донатов"
    ))


def register(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["admin"], state="*", role=UserRole.ADMIN)
