import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.webhook import configure_app, web
from aiogram.utils.exceptions import RetryAfter

from dotenv import load_dotenv
if __name__ == "__main__":
    load_dotenv(".env")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.pool import QueuePool

from tgbot.config import load_config
from tgbot.database.tables import metadata
from tgbot.filters.role import RoleFilter, AdminFilter
from tgbot.handlers.admin import register_admin
from tgbot.handlers.user import register_user
from tgbot.handlers.exam import register_exam
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.role import RoleMiddleware
from tgbot.middlewares.locale import i18n

logger = logging.getLogger(__name__)


async def create_pool(database_url, echo) -> AsyncEngine:
    engine = create_async_engine(
        database_url, pool_size=20, max_overflow=0, poolclass=QueuePool, echo=echo
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    return engine


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    # Load config
    config = load_config()

    # Setup FSM storage
    if config.tg_bot.use_redis:
        storage = RedisStorage2()
    else:
        storage = MemoryStorage()

    # Create database connection pool
    pool = await create_pool(
        database_url=config.db.database_url,
        echo=False,
    )

    # Create bot instance
    bot = Bot(token=config.tg_bot.token, parse_mode="html")
    # Create Dispatcher instance
    dp = Dispatcher(bot, storage=storage)

    dp.middleware.setup(i18n)
    dp.middleware.setup(DbMiddleware(pool))
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admin_id))
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    register_admin(dp)
    register_user(dp)
    register_exam(dp)

    # start
    if not config.webhook.domain:
        try:
            await dp.start_polling()

        finally:
            await dp.storage.close()
            await dp.storage.wait_closed()
            await bot.session.close()

    else:
        await bot.set_webhook(config.webhook.domain + config.webhook.path)
        app = web.Application()
        app["bot"] = bot
        app["config"] = config
        app["dp"] = dp

        app.on_startup.append(on_startup)
        app.on_shutdown.append(on_shutdown)

        configure_app(
            dispatcher=dp,
            app=app,
            path="/bot",
            route_name="bot-webhook"
        )


async def on_startup(app: web.Application):
    while True:
        try:
            await app["bot"].set_webhook(
                app["config"].webhook.domain + app["config"].webhook.path
            )

        except RetryAfter as e:
            logger.warning(f"Flood wait for {e.timeout} sec")
            await asyncio.sleep(e.timeout)

        else:
            break


async def on_shutdown(app: web.Application):
    await app["dp"].storage.close()
    await app["dp"].storage.wait_closed()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
