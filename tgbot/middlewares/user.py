from aiogram.dispatcher.dispatcher import Dispatcher
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types import CallbackQuery
from tgbot.services.repository import Repo


class UserMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ["error", "update"]

    def __init__(self, dp: Dispatcher):
        super().__init__()
        self._dp = dp

    async def pre_process(self, obj, data, *args):
        if not getattr(obj, "from_user", None):
            data["user"] = None
            return
        repo: Repo = data["repo"]
        chat = obj.message.chat if isinstance(obj, CallbackQuery) else obj.chat
        user = {
            "user_id": obj.from_user.id,
            "chat_id": str(chat.id) if chat.id else None,
        }
        user["menu_message_id"] = await repo.get_menu_message_id(user["user_id"], user["chat_id"])
        user["is_banned"] = await repo.get_banned(user["user_id"])
        current_state = await self._dp.current_state().get_state()
        user["state"] = current_state.split(":")[1] if current_state else None
        data["user"] = user

    async def post_process(self, obj, data, *args):
        del data["user"]
