from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import exam_start, menu_explorer
from tgbot.middlewares.locale import i18n as t


def get_kb():
    keyboard = InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        InlineKeyboardButton(
            text=t("Руководителей и главных специалистов"),
            callback_data=exam_start.new("Leaders")
        ),
        InlineKeyboardButton(
            text=t("Инженерно-технических работников"),
            callback_data=exam_start.new("ITR")
        ),
        InlineKeyboardButton(
            text=t("Рабочих специальностей"),
            callback_data=exam_start.new("Workers")
        ),
        InlineKeyboardButton(
            text=t("Контрольные вопросы"),
            callback_data=menu_explorer.new("sec_quest")
        ),
    )

    return keyboard
