import asyncio
import logging

import aioredis
from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.user import UserMiddleware
from tgbot.middlewares.metrics import MetricsMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.handlers.throttling import register_throttling
from tgbot.handlers.menu import register_menu
from tgbot.handlers.support_chat import register_support_chat
from tgbot.utils.bot import get_handled_updates_list
from tgbot.utils.db import create_db_pool


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    config = load_config("bot.ini")

    if config.tg_bot.use_redis:
        storage = RedisStorage2()
    else:
        storage = MemoryStorage()
    db_pool = await create_db_pool(
        user=config.db.user,
        password=config.db.password,
        database=config.db.database,
        host=config.db.host,
    )
    redis_pool = aioredis.from_url("redis://localhost")
    bot = Bot(token=config.tg_bot.token, parse_mode=ParseMode.HTML)
    bot["support_chat_id"] = config.tg_bot.support_chat_id
    dp = Dispatcher(bot, storage=storage)
    dp.middleware.setup(DbMiddleware(db_pool, redis_pool)) # db_pool,
    dp.middleware.setup(UserMiddleware(dp))
    dp.middleware.setup(MetricsMiddleware(enable_metrics=config.tg_bot.enable_metrics))
    dp.middleware.setup(ThrottlingMiddleware())

    register_throttling(dp)
    register_menu(dp, config.tg_bot.support_chat_id)
    register_support_chat(dp, config.tg_bot.support_chat_id)
    
    try:
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await redis_pool.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
