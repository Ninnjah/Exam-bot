from io import BytesIO

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
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
            await m.answer(msg_text)

    else:
        await m.answer(_("Еще никто не пользовался ботом"))


async def list_statistics(m: Message, repo: Repo):
    args = m.get_args().split()
    stats = await repo.list_statistics()

    if args and args[0] == "file" and stats:
        csv_file: BytesIO = BytesIO()
        csv_text: str = "id,user_id,ticket_number,ticket_category," \
                        "tip_count,questions,score,correctness," \
                        "success,time_spent,start_time,created_on\n"

        for num, stat in enumerate(stats, start=1):
            csv_text += f"{num},{stat.user_id},{stat.ticket_number},\"{stat.ticket_category}\"," \
                        f"{stat.tip_count},{stat.questions},{stat.score},{stat.correctness}," \
                        f"{stat.success},{stat.time_spent},{stat.start_time},{stat.created_on}\n"

        csv_file.write(csv_text.encode("utf-8"))
        csv_file.seek(0)

        await m.answer_document(InputFile(csv_file, "user_stats.csv"))
        return

    elif args and args[0] == "plot" and stats:
        plot_file = plotter.tickets_plot(stats)

        await m.answer_photo(InputFile(plot_file, filename="stats.png"))
        return

    elif stats:
        msg_text = _("Статистика решения билетов:\n")
        for num, stat in enumerate(stats, start=1):
            msg_text += _(
                "{num}. <code>{user_id}</code> {ticket_num}:{ticket_cat}"
                " {score}/{questions}({correct:.2f}%) "
                "{spent:.0f} сек. [{start_time}]\n"
            ).format(
                num=num,
                user_id=stat.user_id,
                ticket_num=stat.ticket_number,
                ticket_cat=stat.ticket_category,
                score=stat.score,
                questions=stat.questions,
                correct=stat.correctness,
                spent=stat.time_spent,
                start_time=stat.start_time.strftime("%Y.%m.%d %H:%M")
            )

        if len(msg_text) > parts.MAX_MESSAGE_LENGTH:
            for message in parts.safe_split_text(msg_text, split_separator="\n"):
                await m.answer(message)

        else:
            await m.answer(msg_text)

    else:
        await m.answer(_("Еще никто не решал билеты"))


async def set_config(m: Message, repo: Repo):
    args = m.get_args().split()
    if len(args) != 2:
        await m.answer(_("Неверное количество аргументов!"))
        return

    await repo.add_config(parameter=args[0], value=args[1])
    await m.answer(_(
        "Настройка <code>{parameter}={value}</code> сохранена"
    ).format(
        parameter=args[0],
        value=args[1]
    ))


def register_admin(dp: Dispatcher):
    dp.register_message_handler(list_users, commands=["users"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(list_statistics, commands=["stats"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(set_config, commands=["set"], state="*", role=UserRole.ADMIN)
