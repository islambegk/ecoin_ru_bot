from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.types.callback_query import CallbackQuery

from tgbot.filters.throttled import ThrottledFilter
from tgbot.utils.bot import rerender_menu


async def on_message(message: Message, user, throttled):
    if throttled > 1:
        return

    await message.reply("Превышен лимит сообщений, просим Вас немного подождать!")
    return await rerender_menu(message.bot, user)


async def on_callback_query(cb_query: CallbackQuery, throttled):
    if throttled > 1:
        return
    return await cb_query.answer(f"Слишком много запросов")


def register_throttling(dp: Dispatcher):
    dp.register_message_handler(on_message, ThrottledFilter(), content_types=ContentTypes.ANY, state="*")
    dp.register_callback_query_handler(on_callback_query, ThrottledFilter(), state="*")
