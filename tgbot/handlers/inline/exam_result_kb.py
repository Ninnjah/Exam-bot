from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import exam_result_cb
from tgbot.middlewares.locale import _


def get_kb():
    keyboard = InlineKeyboardMarkup()

    keyboard.add(
        InlineKeyboardButton(
            text=_("Показать результаты"),
            callback_data=exam_result_cb.new()
        )
    )

    return keyboard
