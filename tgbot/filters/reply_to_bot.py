from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter


class ReplyToBotFilter(BoundFilter):
    key = "is_reply_to_bot"

    def __init__(self, is_reply_to_bot: bool):
        self.is_reply_to_bot = is_reply_to_bot

    async def check(self, message: Message):
        if "reply_to_message" not in message:
            return False

        return message.reply_to_message["from"].is_bot is self.is_reply_to_bot
