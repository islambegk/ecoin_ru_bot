from tgbot.constants import UPDATE_TYPES
import time
from datetime import datetime
from cachetools import TTLCache
from cachetools.keys import hashkey

from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware
from aiogram.types import Update, update

from tgbot.services.repository import Repo


class ThrottlingMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]
    throttled_cache = TTLCache(256, 0.5)

    def __init__(self):
        super().__init__()
    
    async def pre_process(self, obj, data, *args):
        user = data["user"]
        metrics = data["metrics"]

        ttl_cache_key = hashkey(user_id=user["user_id"], chat_id=user["user_id"], update_type=metrics["update_type"])
        data["throttled"] = self.throttled_cache.get(ttl_cache_key, -1) + 1
        self.throttled_cache[ttl_cache_key] = data["throttled"]

        if data["throttled"] > 0:
            metrics["action"] = "throttled"

    async def post_process(self, obj, data, *args):
        if "throttled" in data:
            del data["throttled"]
