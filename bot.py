import asyncio
import json
import logging
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.webhook import configure_app, web
from aiogram.utils.exceptions import RetryAfter

from aiohttp.web_request import Request

from aioredis.connection import ConnectionPool

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
config = load_config()

if config.tg_bot.use_redis:
    redis = ConnectionPool.from_url(config.redis.url)
    storage = RedisStorage2(**redis.connection_kwargs)

else:
    storage = MemoryStorage()

bot = Bot(token=config.tg_bot.token, parse_mode="html")
dp = Dispatcher(bot, storage=storage)

# webhook settings
WEBHOOK_HOST = "https://polyer-exam-bot.herokuapp.com"
WEBHOOK_PATH = "/bot"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = "0.0.0.0"  # or ip
WEBAPP_PORT = int(getenv("PORT", default=5000))


async def get_webhook(request: Request):
    data = await request.json()
    logger.info(f"WEBHOOK RECEIVED DATA: {data}")
    try:
        return web.Response(text=json.dumps({"status": "success"}), status=200)

    except Exception as e:
        logger.error(f"GET WEBHOOK ERROR: {e}")
        return web.Response(text=json.dumps({"status": "failed"}), status=500)


async def create_pool(database_url, echo) -> AsyncEngine:
    engine = create_async_engine(
        database_url, pool_size=20, max_overflow=0, poolclass=QueuePool, echo=echo
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    return engine


async def polling_start():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    pool = await create_pool(
        database_url=config.db.database_url,
        echo=False,
    )

    dp.middleware.setup(i18n)
    dp.middleware.setup(DbMiddleware(pool))
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admin_id))
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    register_admin(dp)
    register_user(dp)
    register_exam(dp)

    # start
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


async def on_startup(app: web.Application):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    pool = await create_pool(
        database_url=config.db.database_url,
        echo=False,
    )

    dp.middleware.setup(i18n)
    dp.middleware.setup(DbMiddleware(pool))
    dp.middleware.setup(RoleMiddleware(config.tg_bot.admin_id))
    dp.filters_factory.bind(RoleFilter)
    dp.filters_factory.bind(AdminFilter)

    register_admin(dp)
    register_user(dp)
    register_exam(dp)

    while True:
        try:
            await bot.set_webhook(WEBHOOK_URL)

        except RetryAfter as e:
            logger.warning(f"Flood wait for {e.timeout} sec")
            await asyncio.sleep(e.timeout)

        else:
            break


async def on_shutdown(app: web.Application):
    logging.warning('Shutting down..')

    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


if __name__ == '__main__':
    try:
        asyncio.run(polling_start())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")

else:
    app = web.Application()

    app.router.add_post("/webhook", get_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    configure_app(
        dispatcher=dp,
        app=app,
        path="/bot",
        route_name="bot-webhook"
    )
