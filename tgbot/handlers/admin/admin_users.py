from aiogram import Dispatcher
from aiogram.types import Message, InputFile
from aiogram.utils import parts

from tgbot.middlewares.locale import _
from tgbot.models.role import UserRole
from tgbot.services import plotter
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

        if len(msg_text) > parts.MAX_MESSAGE_LENGTH:
            for message in parts.safe_split_text(msg_text, split_separator="\n"):
                await m.answer(message)

    else:
        await m.answer(_("Еще никто не пользовался ботом"))


async def graph_users(m: Message, repo: Repo):
    users = await repo.list_users()
    plot_file = plotter.users_stat(users)
    await m.answer_photo(InputFile(plot_file, filename="users_stat.png"))


def register(dp: Dispatcher):
    dp.register_message_handler(list_users, commands=["users"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(graph_users, commands=["users_graph"], state="*", role=UserRole.ADMIN)
