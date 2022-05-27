from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import exam_start_cb, menu_explorer_cb
from tgbot.middlewares.locale import _


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=_("Трудовоe законодательство"),
            callback_data=exam_start_cb.new(
                category="Tests", ticket=1
            )
        ),
        InlineKeyboardButton(
            text=_("Обучение по охране труда"),
            callback_data=exam_start_cb.new(
                category="Tests", ticket=2
            )
        ),
        InlineKeyboardButton(
            text=_("Учет и расследование несчастных случаев"),
            callback_data=exam_start_cb.new(
                category="Tests", ticket=3
            )
        ),
        InlineKeyboardButton(
            text=_("Назад"),
            callback_data=menu_explorer_cb.new("main_menu")
        ),
    )

    return keyboard
