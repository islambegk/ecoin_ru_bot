from aiogram import Dispatcher
from aiogram.bot import Bot
from aiogram.utils.exceptions import MessageNotModified

from tgbot.views.menu import menu


async def rerender_menu(bot: Bot, user):
    current_state = user["state"]
    try:
        await bot.edit_message_reply_markup(user["chat_id"], user["menu_message_id"])
    except MessageNotModified:
        pass
    sent_message = await bot.send_message(user["chat_id"], **menu[current_state])
    user["menu_message_id"] = sent_message.message_id


def get_handled_updates_list(dp: Dispatcher) -> list:
    available_updates = (
        "callback_query_handlers", "channel_post_handlers", "chat_member_handlers",
        "chosen_inline_result_handlers", "edited_channel_post_handlers", "edited_message_handlers",
        "inline_query_handlers", "message_handlers", "my_chat_member_handlers", "poll_answer_handlers",
        "poll_handlers", "pre_checkout_query_handlers", "shipping_query_handlers"
    )
    return [item.replace("_handlers", "") for item in available_updates
            if len(dp.__getattribute__(item).handlers) > 0]
