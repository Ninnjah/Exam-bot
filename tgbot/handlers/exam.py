import random
from pathlib import Path
from typing import Dict

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.cb_data import cat_select_cb, show_ticket_cb, exam_start_cb
from tgbot.handlers.inline import tickets_kb, ticket_confirm_kb
from tgbot.middlewares.locale import i18n as t

ASSETS_PATH = Path("assets")


async def select_ticket(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await state.reset_state()
    # Test category (directory name)
    category: str = callback_data.get("category")
    category_path = Path("exam", category)

    ticket_count = len([x for x in category_path.iterdir()])
    await state.update_data(category=category, ticket_count=ticket_count)

    await callback.message.edit_caption(
        caption=t("Выберите билет:"),
        reply_markup=tickets_kb.get_kb(category, ticket_count)
    )


async def ticket_show(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    state_data: dict = await state.get_data()
    category: str = state_data.get("category")
    ticket_count: int = state_data.get("ticket_count")

    ticket_data = callback_data.get("ticket")

    if ticket_data == "random":
        ticket_number = random.randint(1, ticket_count)

    else:
        ticket_number = int(ticket_data)

    await callback.message.answer(
        t("Ваш билет №{ticket}").format(ticket=ticket_number),
        reply_markup=ticket_confirm_kb.get_kb(category, ticket_number)
    )


def register_exam(dp: Dispatcher):
    dp.register_callback_query_handler(
        select_ticket, cat_select_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        ticket_show, show_ticket_cb.filter(), state="*"
    )