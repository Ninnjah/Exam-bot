from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.cb_data import ticket_choose_cb, menu_explorer_cb
from tgbot.middlewares.locale import i18n as t


def get_kb(category: str, ticket_count: int):
    keyboard = InlineKeyboardMarkup()

    for ticket_number in range(1, ticket_count + 1):
        keyboard.insert(
            InlineKeyboardButton(
                text=str(ticket_number),
                callback_data=ticket_choose_cb.new(
                    category=category, number=ticket_number
                )
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=t("Случайный билет"),
            callback_data=ticket_choose_cb.new(
                category=category, number="random"
            )
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text=t("Назад"),
            callback_data=menu_explorer_cb.new("main_menu")
        )
    )

    return keyboard
