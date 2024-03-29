from datetime import datetime
import random
from pathlib import Path
import logging
from typing import List, Dict

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InputFile
from aiogram.utils.exceptions import MessageCantBeDeleted, \
    MessageToDeleteNotFound, MessageNotModified, BadRequest

from telegraph.exceptions import TelegraphException

from tgbot.cb_data import cat_select_cb, show_ticket_cb, exam_start_cb, \
    ticket_cancel_cb, exam_answer_cb, get_tip_cb, exam_result_cb, delete_cb
from tgbot.handlers.inline import tickets_kb, ticket_confirm_kb, exam_answer_kb, \
    exam_result_kb, delete_kb, exam_end_kb
from tgbot.middlewares.locale import _
from tgbot.services.number_decl import get_declination
from tgbot.services.repository import Repo
from tgbot.services.ticket_parser import parse_ticket
from tgbot.services.telegraph_create import create_page

logger = logging.getLogger(__name__)


async def ticket_select(
        callback: CallbackQuery,
        callback_data: Dict[str, str],
        repo: Repo,
        state: FSMContext
):
    await state.reset_state()
    # Test category (directory name)
    category: str = callback_data.get("category")
    category_path = Path("exam", category)

    ticket_count = len([x for x in category_path.iterdir()])
    await state.update_data(category=category, ticket_count=ticket_count)

    try:
        await callback.message.edit_caption(
            caption=_("Выберите билет:"),
            reply_markup=tickets_kb.get_kb(category, ticket_count)
        )

    except MessageNotModified:
        asset = await repo.get_asset("main_menu")
        if asset:
            file_id = asset.file_id
            await callback.message.answer_photo(
                file_id,
                _("Выберите билет:"),
                reply_markup=tickets_kb.get_kb(category, ticket_count)
            )

        else:
            await callback.message.answer(
                _("Выберите билет:"),
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
        _("Ваш билет №{ticket}").format(ticket=ticket_number),
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
            caption=_("Выберите билет:"),
            reply_markup=tickets_kb.get_kb(category, ticket_count)
        )

    except MessageToDeleteNotFound:
        pass


async def ticket_start(callback: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    # get ticket category and number from state storage
    state_data: dict = await state.get_data()
    category: str = state_data.get("category") \
        if state_data.get("category") is not None \
        else callback_data.get("category")
    ticket_number: int = int(callback_data.get("ticket"))

    # Current question index
    question_index: int = 0
    # Load ticket questions
    ticket: List[dict] = parse_ticket(f"exam/{category}/Paper_{ticket_number}.xml")
    # Save current question number, ticket number, start time
    # and ticket data in state storage and set state score and tip count to zero
    await state.update_data(
        ticket_number=ticket_number,
        start_time=datetime.now().timestamp(),
        ticket=ticket,
        index=question_index,
        score=0,
        tip_count=0
    )

    # Get current question
    current_ticket = ticket[question_index]
    # Get answers for current question
    answers = current_ticket.get("answers")
    # Question text
    msg_text: str = current_ticket.get("text") + "\n\n"

    # Answer option texts with numeric
    for num, answer in enumerate(answers.keys(), start=1):
        msg_text += f"<b>{num}.</b> {answer}\n\n"

    try:
        await callback.message.edit_text(
            msg_text,
            reply_markup=exam_answer_kb.get_kb(answers.values())
        )

    except MessageNotModified:
        await callback.message.answer(
            msg_text,
            reply_markup=exam_answer_kb.get_kb(answers.values())
        )

    except BadRequest:
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

    # Save current question number and ticket data in state storage and set state score to zero
    await state.update_data(index=question_index + 1, score=state_score + score)

    # Check correctness of the answer
    if score:
        await callback.answer(text=_("Правильно!"), show_alert=False)

    else:
        await callback.answer(text=_("Неправильно!️"), show_alert=False)
        msg_text += _(
            "<b>Правильный ответ на предыдущий вопрос:</b>️\n<i>{correct}</i>\n\n"
        ).format(
            correct=correct_answer
        )

    # If previous question was last
    if question_index + 1 >= len(ticket):
        msg_text += _("Вы закончили!")

        try:
            await callback.message.edit_text(
                msg_text,
                reply_markup=exam_result_kb.get_kb()
            )

        except MessageNotModified:
            await callback.message.answer(
                msg_text,
                reply_markup=exam_result_kb.get_kb()
            )

        finally:
            return

    # Get current question
    current_ticket = ticket[question_index + 1]
    # Get answers for current question
    answers = current_ticket.get("answers")

    # Question text
    msg_text += _("{question}\n\n").format(
        question=current_ticket.get("text")
    )

    # Answer option texts with numeric
    for num, answer in enumerate(answers.keys(), start=1):
        msg_text += f"<b>{num}.</b> {answer}\n\n"

    try:
        await callback.message.edit_text(
            msg_text,
            reply_markup=exam_answer_kb.get_kb(answers.values())
        )

    except MessageNotModified:
        await callback.message.answer(
            msg_text,
            reply_markup=exam_answer_kb.get_kb(answers.values())
        )

    await callback.answer()


async def show_tip(callback: CallbackQuery, state: FSMContext, repo: Repo):
    # Get ticket data, current question number and score from state storage
    state_data = await state.get_data()
    ticket = state_data.get("ticket")
    question_index = state_data.get("index")

    # Increase tip count
    tip_count = state_data.get("tip_count")
    await state.update_data(tip_count=tip_count + 1)

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


async def exam_result(callback: CallbackQuery, repo: Repo, state: FSMContext):
    # Get ticket data, current question number and score from state storage
    state_data = await state.get_data()
    ticket = state_data.get("ticket")

    ticket_number: int = state_data.get("ticket_number")
    category: str = state_data.get("category")
    tip_count: int = state_data.get("tip_count")
    current_score: int = state_data.get("score")
    start_time: datetime = datetime.fromtimestamp(state_data.get("start_time"))
    time_spent: float = (datetime.now() - start_time).total_seconds()

    payment = await repo.get_config("donate_link")

    # Get number of questions (number of correct answers)
    max_score = len(ticket)

    success: bool = True if current_score == max_score else False

    minutes_declines: list = _("минута минуты минут").split()
    seconds_declines: list = _("секунда секунды секунд").split()

    if time_spent <= 60:
        sec_string: str = get_declination(time_spent, seconds_declines)

        time_spent_string: str = f"{time_spent:.0f} {sec_string}"
    else:
        minutes: int = int(time_spent // 60)
        seconds: int = int(time_spent - minutes * 60)

        min_string: str = get_declination(minutes, minutes_declines)
        sec_string: str = get_declination(seconds, seconds_declines)

        time_spent_string: str = f"{minutes} {min_string} {seconds} {sec_string}"

    if success:
        try:
            await callback.message.edit_text(_(
                "Экзамен сдан!\n"
                "Вы ответили на {score} из {max_score}\n"
                "Правильность ответов: {correctness:.0f}%\n"
                "Вы потратили: {time_spent}"
            ).format(
                score=current_score,
                max_score=max_score,
                correctness=(current_score / max_score) * 100,
                time_spent=time_spent_string
            ),
                reply_markup=exam_end_kb.get_kb(payment.link)
            )

        except MessageNotModified:
            await callback.message.answer(_(
                "Экзамен сдан!\n"
                "Вы ответили на {score} из {max_score}\n"
                "Правильность ответов: {correctness:.0f}%\n"
                "Вы потратили: {time_spent}"
            ).format(
                score=current_score,
                max_score=max_score,
                correctness=(current_score / max_score) * 100,
                time_spent=time_spent_string
            ),
                reply_markup=exam_end_kb.get_kb(payment.link)
            )

    else:
        try:
            await callback.message.edit_text(_(
                "Экзамен не сдан!\n"
                "Вы ответили на {score} из {max_score}\n"
                "Правильность ответов: {correctness:.0f}%\n"
                "Вы потратили: {time_spent}"
            ).format(
                score=current_score,
                max_score=max_score,
                correctness=(current_score / max_score) * 100,
                time_spent=time_spent_string
            ),
                reply_markup=exam_end_kb.get_kb(payment)
            )

        except MessageNotModified:
            await callback.message.answer(_(
                "Экзамен не сдан!\n"
                "Вы ответили на {score} из {max_score}\n"
                "Правильность ответов: {correctness:.0f}%\n"
                "Вы потратили: {time_spent}"
            ).format(
                score=current_score,
                max_score=max_score,
                correctness=(current_score / max_score) * 100,
                time_spent=time_spent_string
            ),
                reply_markup=exam_end_kb.get_kb(payment.link)
            )

    # Save statistic
    await repo.add_statistic(
        callback.from_user.id,
        ticket_number=ticket_number,
        ticket_category=category,
        tip_count=tip_count,
        questions=max_score,
        score=current_score,
        success=success,
        time_spent=time_spent,
        start_time=start_time
    )
    await repo.add_user(
        callback.from_user.id,
        callback.from_user.first_name,
        callback.from_user.last_name,
        callback.from_user.username
    )


def register(dp: Dispatcher):
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
    dp.register_callback_query_handler(
        exam_result, exam_result_cb.filter(), state="*"
    )
