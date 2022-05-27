from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import exam_start_cb, ticket_cancel_cb
from tgbot.middlewares.locale import _


def get_kb(category: str, ticket_number: int):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text=_("Начать"),
            callback_data=exam_start_cb.new(
                category=category, ticket=ticket_number
            )
        ),
        InlineKeyboardButton(
            text=_("Отмена"),
            callback_data=ticket_cancel_cb.new()
        ),
    )

    return keyboard
