from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import delete_cb
from tgbot.middlewares.locale import i18n as t


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=t("Удалить"),
            callback_data=delete_cb.new()
        ),
    )

    return keyboard
