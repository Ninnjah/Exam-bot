import random
from pathlib import Path
import logging
from typing import List, Dict

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

from telegraph.exceptions import TelegraphException

from tgbot.cb_data import cat_select_cb, show_ticket_cb, exam_start_cb, \
    ticket_cancel_cb, exam_answer_cb, get_tip_cb, exam_result_cb, delete_cb
from tgbot.handlers.inline import tickets_kb, ticket_confirm_kb, exam_answer_kb, \
    exam_result_kb, delete_kb
from tgbot.middlewares.locale import i18n as t
from tgbot.services.repository import Repo
from tgbot.services.ticket_parser import parse_ticket
from tgbot.services.telegraph_create import create_page

logger = logging.getLogger(__name__)


async def ticket_select(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await state.reset_state()
    # Test category (directory name)
    category: str = callback_data.get("category")
    category_path = Path("exam", category)

    ticket_count = len([x for x in category_path.iterdir()])
    await state.update_data(category=category, ticket_count=ticket_count)

    await callback.message.edit_caption(
        caption=t("Выберите билет:"),
        reply_markup=tickets_kb.get_kb(category, ticket_count)
    )


async def ticket_show(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    # get ticket category and ticket count from state storage
    state_data: dict = await state.get_data()
    category: str = state_data.get("category")
    ticket_count: int = state_data.get("ticket_count")

    # Get ticket number from callback data
    ticket_data = callback_data.get("ticket")

    if ticket_data == "random":
        ticket_number = random.randint(1, ticket_count)

    else:
        ticket_number = int(ticket_data)

    await callback.message.answer(
        t("Ваш билет №{ticket}").format(ticket=ticket_number),
        reply_markup=ticket_confirm_kb.get_kb(category, ticket_number)
    )


async def ticket_cancel(callback: CallbackQuery, state: FSMContext, repo: Repo):
    state_data: dict = await state.get_data()
    category: str = state_data.get("category")
    ticket_count: int = state_data.get("ticket_count")

    try:
        await callback.message.delete()

    except MessageCantBeDeleted:
        asset = await repo.get_asset("main_menu")
        await callback.message.answer_photo(
            asset.file_id,
            caption=t("Выберите билет:"),
            reply_markup=tickets_kb.get_kb(category, ticket_count)
        )

    except MessageToDeleteNotFound:
        pass


async def ticket_start(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    # get ticket category and number from state storage
    state_data: dict = await state.get_data()
    category: str = state_data.get("category")
    ticket_number: int = int(callback_data.get("ticket"))

    # Current question index
    question_index: int = 0
    # Load ticket questions
    ticket: List[dict] = parse_ticket(f"exam/{category}/Paper_{ticket_number}.xml")
    # Save current question number and ticket data in state storage and set state score to zero
    await state.update_data(ticket=ticket, index=question_index, score=0)

    # Get current question
    current_ticket = ticket[question_index]
    # Get answers for current question
    answers = current_ticket.get("answers")
    # Question text
    msg_text: str = current_ticket.get("text") + "\n\n"

    # Answer option texts with numeric
    for num, answer in enumerate(answers.keys(), start=1):
        msg_text += f"<b>{num}.</b> {answer}\n\n"

    await callback.message.answer(
        msg_text,
        reply_markup=exam_answer_kb.get_kb(answers.values())
    )


async def ticket_answer(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    # Get ticket data, current question number and score from state storage
    state_data = await state.get_data()
    ticket = state_data.get("ticket")
    question_index = state_data.get("index")
    state_score = state_data.get("score")
    msg_text: str = ""

    # Get answer score from callback data
    score = int(callback_data.get("score"))

    # Get correct answer for previous question
    previous_question = ticket[question_index]
    prev_answers = previous_question.get("answers")
    correct_answer = list(prev_answers.keys())[list(prev_answers.values()).index(1)]

    # Check correctness of the answer
    if score:
        await callback.answer(text=t("Правильно!"), show_alert=False)

    else:
        await callback.answer(text=t("Неправильно!️"), show_alert=False)
        msg_text += t(
            "<b>Правильный ответ на предыдущий вопрос:</b>️\n<i>{correct}</i>\n\n"
        ).format(
            correct=correct_answer
        )

    # If previous question was last
    if question_index + 1 >= len(ticket):
        msg_text += t("Вы закончили!")

        await callback.message.edit_text(
            msg_text,
            reply_markup=exam_result_kb.get_kb()
        )
        return

    # Get current question
    current_ticket = ticket[question_index + 1]
    # Get answers for current question
    answers = current_ticket.get("answers")

    # Save current question number and ticket data in state storage and set state score to zero
    await state.update_data(index=question_index + 1, score=state_score + score)

    # Question text
    msg_text += current_ticket.get("text") + "\n\n"

    # Answer option texts with numeric
    for num, answer in enumerate(answers.keys(), start=1):
        msg_text += f"<b>{num}.</b> {answer}\n\n"

    await callback.message.edit_text(
        msg_text,
        reply_markup=exam_answer_kb.get_kb(answers.values())
    )


async def show_tip(callback: CallbackQuery, state: FSMContext, repo: Repo):
    # Get ticket data, current question number and score from state storage
    state_data = await state.get_data()
    ticket = state_data.get("ticket")
    question_index = state_data.get("index")

    # Get question tip
    tip: str = ticket[question_index].get("info")
    info_file = str(Path("Info", *tip.split("\\")))

    if '.rtf' in tip:
        title = tip.split('.')[-2].strip()
        link = await repo.get_page(title)

        if link is not None:
            await callback.message.reply(link[0], reply_markup=delete_kb.get_kb())

        else:
            try:
                link = await create_page(filename=info_file, title=title)

            except TelegraphException as e:
                logger.error(f"CREATE_PAGE: {e}", exc_info=True)
                with open(info_file, 'rb') as f:
                    await callback.message.reply_document(f, reply_markup=delete_kb.get_kb())

            else:
                await repo.add_page(title, link)
                await callback.message.reply(
                    link,
                    reply_markup=delete_kb.get_kb()
                )

    else:
        asset = await repo.get_asset(tip)
        if asset:
            if '.png' in tip:
                await callback.message.reply_photo(
                    asset.file_id,
                    reply_markup=delete_kb.get_kb()
                )
            else:
                await callback.message.reply_document(
                    asset.file_id,
                    reply_markup=delete_kb.get_kb()
                )

        else:
            file_id = InputFile(info_file)
            if '.png' in tip:
                message = await callback.message.reply_photo(
                    file_id,
                    reply_markup=delete_kb.get_kb()
                )
                await repo.add_asset(info_file, message.photo[-1].file_id)

            else:
                message = await callback.message.reply_document(
                    file_id,
                    reply_markup=delete_kb.get_kb()
                )
                await repo.add_asset(info_file, message.document.file_id)


async def delete_tip(callback: CallbackQuery):
    try:
        await callback.message.delete()

    except MessageCantBeDeleted:
        pass

    except MessageToDeleteNotFound:
        pass


def register_exam(dp: Dispatcher):
    dp.register_callback_query_handler(
        ticket_select, cat_select_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        ticket_show, show_ticket_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        ticket_cancel, ticket_cancel_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        ticket_start, exam_start_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        ticket_answer, exam_answer_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        show_tip, get_tip_cb.filter(), state="*"
    )
    dp.register_callback_query_handler(
        delete_tip, delete_cb.filter(), state="*"
    )
