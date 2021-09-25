from tgbot.constants import UPDATE_TYPES
import time
from datetime import datetime

from aiogram.dispatcher.middlewares import BaseMiddleware, LifetimeControllerMiddleware
from aiogram.types import Update

from tgbot.services.repository import Repo


class MetricsMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, enable_metrics: bool):
        super().__init__()
        self._enable_metrics = enable_metrics

    

    async def pre_process(self, obj, data, *args):
        if not self._enable_metrics:
            return

        current_update = Update.get_current()
        update_type = "unknown"
        for type in UPDATE_TYPES:
            if type in current_update:
                update_type = type

        data["metrics"] = {
            "timestamp": datetime.now(),
            "start_time": time.monotonic(),
            "update_type": update_type,
            "user_id": data["user"]["user_id"],
            "chat_id": data["user"]["chat_id"]
        }

    async def post_process(self, obj, data, *args):
        if "metrics" in data:
            del data["metrics"]
