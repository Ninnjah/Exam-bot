from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import exam_answer_cb, get_tip_cb
from tgbot.middlewares.locale import i18n as t


def get_kb(answers_scores: list):
    keyboard = InlineKeyboardMarkup()

    for num, score in enumerate(answers_scores, start=1):
        keyboard.insert(
            InlineKeyboardButton(
                text=str(num),
                callback_data=exam_answer_cb.new(score)
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=t("Подсказка"),
            callback_data=get_tip_cb.new()
        )
    )

    return keyboard
