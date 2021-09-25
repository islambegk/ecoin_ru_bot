import time
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from tgbot.services.repository import Repo


class DbMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, db_pool, redis_pool):
        super().__init__()
        self._db_pool = db_pool
        self._redis_pool = redis_pool

    async def pre_process(self, obj, data, *args):
        data["db"] = await self._db_pool.connect()
        data["repo"] = Repo(data["db"], self._redis_pool.client())  # db,

    async def post_process(self, obj, data, *args):
        repo: Repo = data["repo"]
        user = data.get("user", None)
        if user and user["state"] is not None:
            if user["menu_message_id"]:
                await repo.set_menu_message_id(user["menu_message_id"], user["user_id"], user["chat_id"])
            if user["is_banned"] is not None:
                is_banned = 1 if user["is_banned"] else 0
                await repo.set_banned(is_banned, user["user_id"])

        metrics = data.get("metrics", None)
        if metrics:
            metrics["time_delta"] = time.monotonic() - metrics["start_time"]
            del metrics["start_time"]
            await repo.post_metrics(metrics)

        del data["repo"]

        db = data.get("db")
        if db:
            await db.close()
