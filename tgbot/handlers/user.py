from pathlib import Path

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, InputFile

from tgbot.cb_data import menu_explorer_cb
from tgbot.handlers.inline import main_kb, sec_quest_kb
from tgbot.middlewares.locale import _
#from tgbot.services.repository import Repo

ASSETS_PATH = Path("assets")


async def user_start(m: Message):
    #await repo.add_user(
    #    m.from_user.id,
    #    m.from_user.first_name,
    #    m.from_user.last_name,
    #    m.from_user.username
    #)

    #asset = await repo.get_asset("main_menu")
    asset = False
    if asset:
        file_id = asset.file_id
        await m.answer_photo(
            file_id,
            caption=_("Экзаменационные билеты какой специальности вам нужны?"),
            reply_markup=main_kb.get_kb()
        )

    else:
        file_id = InputFile(ASSETS_PATH / Path("main_menu.jpg"))

        message = await m.answer_photo(
            file_id,
            caption=_("Экзаменационные билеты какой специальности вам нужны?"),
            reply_markup=main_kb.get_kb()
        )
        #await repo.add_asset("main_menu", message.photo[0].file_id)


async def return_to_main_menu(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=_("Экзаменационные билеты какой специальности вам нужны?"),
        reply_markup=main_kb.get_kb()
    )


async def control_menu(callback: CallbackQuery):
    await callback.message.edit_caption(
        caption=_("Какие контрольные вопросы вам нужны?"),
        reply_markup=sec_quest_kb.get_kb()
    )


def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")
    dp.register_callback_query_handler(
        return_to_main_menu, menu_explorer_cb.filter(menu="main_menu"), state="*"
    )
    dp.register_callback_query_handler(
        control_menu, menu_explorer_cb.filter(menu="sec_quest"), state="*"
    )
