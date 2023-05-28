from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.middlewares.locale import _


cb = CallbackData("ad_conf", "state", "action")


def get(state: str):
    keyboard = InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        InlineKeyboardButton(
            text=_("Да"),
            callback_data=cb.new(
                state=state,
                action=1
            )
        ),
        InlineKeyboardButton(
            text=_("Нет"),
            callback_data=cb.new(
                state=state,
                action=0
            )
        )
    )

    return keyboard
