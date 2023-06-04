from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from sqlalchemy.engine.row import RowMapping

from tgbot.cb_data import ticket_cancel_cb
from tgbot.middlewares.locale import _


def get_kb(payment: RowMapping):
    keyboard = InlineKeyboardMarkup(row_width=1)

    if payment is not None:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Отблагодарить разработчика"),
                url=payment.get("link")
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=_("Закончить"),
            callback_data=ticket_cancel_cb.new()
        ),
    )

    return keyboard
