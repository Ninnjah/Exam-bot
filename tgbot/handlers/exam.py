from pathlib import Path
from typing import Dict

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from tgbot.cb_data import cat_select_cb
from tgbot.handlers.inline import tickets_kb
from tgbot.middlewares.locale import i18n as t

ASSETS_PATH = Path("assets")


async def select_ticket(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await state.reset_state()
    # Test category (directory name)
    category: str = callback_data.get("type")
    category_path = Path("exam", category)

    ticket_count = len([x for x in category_path.iterdir()])

    await callback.message.edit_caption(
        caption=t("Выберите билет:"),
        reply_markup=tickets_kb.get_kb(category, ticket_count)
    )


def register_exam(dp: Dispatcher):
    dp.register_callback_query_handler(select_ticket, cat_select_cb.filter(), state="*")
