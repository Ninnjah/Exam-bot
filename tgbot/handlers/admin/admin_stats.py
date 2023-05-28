from io import BytesIO

from aiogram import Dispatcher
from aiogram.types import Message, InputFile
from aiogram.utils import parts

from tgbot.middlewares.locale import _
from tgbot.models.role import UserRole
from tgbot.services import plotter
from tgbot.services.repository import Repo


async def tickets_stats(m: Message, repo: Repo):
    stats = await repo.list_statistics()
    if not stats:
        await m.answer(_("Еще никто не решал билеты"))
        return

    msg_text = _("Статистика решения билетов:\n")
    for num, stat in enumerate(stats[:50], start=1):
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


async def ticket_csv_stats(m: Message, repo: Repo):
    stats = await repo.list_statistics()
    if not stats:
        await m.answer(_("Еще никто не решал билеты"))
        return

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


async def ticket_plot_stats(m: Message, repo: Repo):
    stats = await repo.list_statistics()
    if not stats:
        await m.answer(_("Еще никто не решал билеты"))
        return

    plot_file = plotter.tickets_stat(stats)
    await m.answer_photo(InputFile(plot_file, filename="stats_all.png"))


async def users_top_stats(m: Message, repo: Repo):
    stats = await repo.list_statistics()
    if not stats:
        await m.answer(_("Еще никто не решал билеты"))
        return

    plot_file = plotter.user_top_plot(stats)
    await m.answer_photo(InputFile(plot_file, filename="user_top.png"))


def register(dp: Dispatcher):
    dp.register_message_handler(tickets_stats, commands=["ticket_stats"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(ticket_csv_stats, commands=["ticket_csv"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(ticket_plot_stats, commands=["ticket_plot"], state="*", role=UserRole.ADMIN)
    dp.register_message_handler(users_top_stats, commands=["users_top"], state="*", role=UserRole.ADMIN)
