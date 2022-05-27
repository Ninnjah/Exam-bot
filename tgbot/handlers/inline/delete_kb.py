from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import delete_cb
from tgbot.middlewares.locale import _


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=_("Удалить"),
            callback_data=delete_cb.new()
        ),
    )

    return keyboard
