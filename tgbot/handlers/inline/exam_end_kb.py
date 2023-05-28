from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import ticket_cancel_cb
from tgbot.middlewares.locale import _


def get_kb(donate_link: str):
    keyboard = InlineKeyboardMarkup(row_width=1)

    if donate_link is not None:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Отблагодарить разработчика"),
                url=donate_link
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=_("Закончить"),
            callback_data=ticket_cancel_cb.new()
        ),
    )

    return keyboard
