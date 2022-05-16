from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import cat_select_cb, menu_explorer_cb
from tgbot.middlewares.locale import i18n as t


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=t("Руководителей и главных специалистов"),
            callback_data=cat_select_cb.new("Leaders")
        ),
        InlineKeyboardButton(
            text=t("Инженерно-технических работников"),
            callback_data=cat_select_cb.new("ITR")
        ),
        InlineKeyboardButton(
            text=t("Рабочих специальностей"),
            callback_data=cat_select_cb.new("Workers")
        ),
        InlineKeyboardButton(
            text=t("Контрольные вопросы"),
            callback_data=menu_explorer_cb.new("sec_quest")
        ),
    )

    return keyboard
