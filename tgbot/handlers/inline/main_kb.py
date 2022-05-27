from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import cat_select_cb, menu_explorer_cb
from tgbot.middlewares.locale import _


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=_("Руководителей и главных специалистов"),
            callback_data=cat_select_cb.new("Leaders")
        ),
        InlineKeyboardButton(
            text=_("Инженерно-технических работников"),
            callback_data=cat_select_cb.new("ITR")
        ),
        InlineKeyboardButton(
            text=_("Рабочих специальностей"),
            callback_data=cat_select_cb.new("Workers")
        ),
        InlineKeyboardButton(
            text=_("Контрольные вопросы"),
            callback_data=menu_explorer_cb.new("sec_quest")
        ),
    )

    return keyboard
