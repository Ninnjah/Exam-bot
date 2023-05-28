from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.handlers.admin.inline import confirm_kb
from tgbot.handlers.admin.states.payments import AdminPayments
from tgbot.middlewares.locale import _
from tgbot.models.role import UserRole
from tgbot.services.repository import Repo


async def query_payment(m: Message, state: FSMContext):
    await state.reset_state()
    await state.set_state(AdminPayments.payment.state)
    await m.answer(_("Отправь ссылку для оплаты"))


async def handle_payment(m: Message, state: FSMContext):
    payment = m.text
    await state.update_data(payment=payment)
    await m.reply(
        _("Добавить эту ссылку, как способ оплаты?"),
        reply_markup=confirm_kb.get("payment")
    )


async def accept_payment(callback: CallbackQuery, repo: Repo, state: FSMContext):
    data = await state.get_data()
    payment = data["payment"]
    title = "donate_link"

    await repo.add_payment(title, payment)
    await state.reset_state()
    await callback.message.answer(_("Способ оплаты добавлен!"))


async def reject_payment(callback: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await callback.message.answer(_("Добавление способа оплаты отменено!"))


def register(dp: Dispatcher):
    dp.register_message_handler(query_payment, commands=["set_payment"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(handle_payment, state=AdminPayments.payment, role=UserRole.ADMIN)
    dp.register_callback_query_handler(
        accept_payment, confirm_kb.cb.filter(state="payment", action="1"),
        state="*", role=UserRole.ADMIN
    )
    dp.register_callback_query_handler(
        reject_payment, confirm_kb.cb.filter(state="payment", action="0"),
        state="*", role=UserRole.ADMIN
    )
