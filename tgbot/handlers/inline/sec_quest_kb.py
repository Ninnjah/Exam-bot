from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import exam_start_cb, menu_explorer_cb
from tgbot.middlewares.locale import i18n as t


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=t("Трудовоe законодательство"),
            callback_data=exam_start_cb.new("Tests_1")
        ),
        InlineKeyboardButton(
            text=t("Обучение по охране труда"),
            callback_data=exam_start_cb.new("Tests_2")
        ),
        InlineKeyboardButton(
            text=t("Учет и расследование несчастных случаев"),
            callback_data=exam_start_cb.new("Tests_3")
        ),
        InlineKeyboardButton(
            text=t("Назад"),
            callback_data=menu_explorer_cb.new("main_menu")
        ),
    )

    return keyboard
