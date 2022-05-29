from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from tgbot.middlewares.locale import _
from tgbot.models.role import UserRole
from tgbot.services.repository import Repo


async def list_users(m: Message, repo: Repo):
    users = await repo.list_users()

    if users:
        msg_text = _("Список пользователей:\n")
        for num, user in enumerate(users, start=1):
            fullname = f"{user.firstname}{' ' + user.lastname if user.lastname is not None else ''}"

            msg_text += _(
                "{num}. <code>{user_id}</code> "
                "<a href='tg://user?id={user_id}'><b>{fullname}</b></a> {username}[{date}]\n"
            ).format(
                num=num,
                user_id=user.user_id,
                fullname=fullname,
                username=f"(@{user.username})" if user.username is not None else "",
                date=user.created_on.strftime("%Y.%m.%d %H:%M")
            )

        await m.answer(msg_text)

    else:
        await m.answer(_("Еще никто не пользовался ботом"))


def register_admin(dp: Dispatcher):
    dp.register_message_handler(list_users, commands=["users"], state="*", role=UserRole.ADMIN)
    # # or you can pass multiple roles:
    # dp.register_message_handler(admin_start, commands=["start"], state="*", role=[UserRole.ADMIN])
    # # or use another filter:
    # dp.register_message_handler(admin_start, commands=["start"], state="*", is_admin=True)
