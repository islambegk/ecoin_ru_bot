from aiogram.types import Message
from aiogram.dispatcher.filters import BoundFilter


class UserQuestionFilter(BoundFilter):
    key = "is_user_question"

    def __init__(self, is_user_question:bool):
        self.is_user_question = is_user_question

    async def check(self, message: Message):
        reply_to_message = message.reply_to_message
        if not reply_to_message:
            return self.is_user_question
        if not message.reply_to_message["from"].is_bot:
            return False
        if reply_to_message.text:
            return (reply_to_message.text.split("\n\n")[0].split(" #")[0] == "Пользователь") is self.is_user_question
        elif reply_to_message.caption:
            return (reply_to_message.caption.split("\n\n")[-1].split(" #")[0] == "Пользователь") is self.is_user_question

        return self.is_user_question
