from typing import Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import ticket_cancel_cb
from tgbot.middlewares.locale import _


def get_kb(donate_link: Optional[dict]):
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=_("Закончить"),
            callback_data=ticket_cancel_cb.new()
        ),
    )

    if donate_link is not None:
        keyboard.add(
            InlineKeyboardButton(
                text=_("Отблагодарить разработчика"),
                url=donate_link.get("value")
            )
        )

    return keyboard
