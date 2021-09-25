from typing import Union
from aiogram import Dispatcher
from aiogram.types import CallbackQuery, Message
from aiogram.types.message import ContentType, ContentTypes
from aiogram.dispatcher.filters import IDFilter
from aiogram.dispatcher.filters.filters import NotFilter

from tgbot.views.menu import menu
from tgbot.utils.bot import rerender_menu
from tgbot.views.states import MenuSG
from tgbot.services.repository import Repo


async def start(message: Message, user: dict, metrics: dict):
    metrics["action"] = "start_main"
    if user["menu_message_id"]:
        return await rerender_menu(message.bot, user)

    await MenuSG.main.set()
    user["state"] = "main"
    sent_message = await message.answer(**menu["main"])
    user["menu_message_id"] = sent_message.message_id


async def send_menu(cb_query: CallbackQuery, metrics: dict):
    cb_data = cb_query["data"]
    metrics["action"] = cb_data
    new_menu = menu[cb_data]
    await cb_query.message.edit_text(new_menu["text"], disable_web_page_preview=True)
    await cb_query.message.edit_reply_markup(new_menu["reply_markup"])
    await cb_query.answer()
    await getattr(MenuSG, cb_data).set()


async def on_text_question(message: Message, user: dict, metrics: dict, repo: Repo):
    metrics["action"] = "question_text"
    if user["is_banned"]:
        await message.answer("К сожалению, ты был заблокирован поддержкой и твои сообщения больше не будут доставлены.")
    elif len(message.text) > 4050:
        await message.reply("К сожалению, длина этого сообщения превышает допустимый размер в 4050 символов. Попробуйте сократить свой вопрос в новом сообщении или отправить его по частям.")
    else:
        support_chat_id = message.bot.get("support_chat_id")
        text_to_forward = f"Пользователь <code>#{message.from_user.id}</code>\n\n{message.html_text}"
        forwarded = await message.bot.send_message(support_chat_id, text_to_forward, disable_web_page_preview=True)
        question_data = {
            "user_id": user["user_id"],
            "chat_id": user["chat_id"],
            "message_id": message["message_id"],
            "state": user["state"]
        }
        await repo.set_question_data(forwarded.message_id, question_data)
        await message.reply("Спасибо за ваш вопрос! Бот переслал его в поддержку.")

    await rerender_menu(message.bot, user)


async def on_supported_media_question(message: Message, user: dict, metrics: dict, repo: Repo):
    metrics["action"] = "question_media"
    if user["is_banned"]:
        await message.answer("К сожалению, Вы были заблокирован поддержкой и твои сообщения больше не будут доставлены.")
    elif 'caption' in message and len(message.caption) > 950:
        await message.reply("К сожалению, длина подписи медиафайла превышает допустимый размер в 1000 символов. Попробуйте сократить её в следующем сообщении или отправить отдельно от самого файла.")
    else:
        support_chat_id = message.bot.get("support_chat_id")
        caption_sent = (message.caption and message.parse_entities(as_html=True)) or ""
        caption_to_forward = f"{caption_sent}\n\nПользователь <code>#{message.from_user.id}</code>"
        forwarded = await message.copy_to(support_chat_id, caption=caption_to_forward)
        question_data = {
            "user_id": user["user_id"],
            "chat_id": user["chat_id"],
            "message_id": message["message_id"],
            "state": user["state"]
        }
        await repo.set_question_data(forwarded.message_id, question_data)
        await message.reply("Спасибо за ваш вопрос! Бот переслал его в поддержку.")

    await rerender_menu(message.bot, user)


async def on_unsupported_types_question(message: Message, user: dict, metrics: dict):
    metrics["action"] = "question_unsupported"
    # Игнорируем служебные сообщения
    if message.content_type in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VOICE_CHAT_STARTED,
            ContentType.VOICE_CHAT_ENDED, ContentType.VOICE_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, ContentType.PROXIMITY_ALERT_TRIGGERED,
            ContentType.NEW_CHAT_TITLE):
        return
    
    await message.reply("К сожалению, этот тип сообщения не поддерживается для пересылки от пользователей. Попробуйте отправить что-нибудь другое.")
    await rerender_menu(message.bot, user)


async def rerender_on_message(message: Message, user: dict):
    return await rerender_menu(message.bot, user)


async def edited_message_warning(message: Message, user: dict, metrics: dict):
    metrics["action"] = "question_edit"
    await message.reply("К сожалению, отредактированное сообщение не будет видно принимающей стороне. Вы можете отправить изменённый текст в новом сообщении.")
    return await rerender_menu(message.bot, user)


def register_menu(dp: Dispatcher, support_chat_id: Union[int, str]):
    not_support_chat_filter = NotFilter(IDFilter(chat_id=support_chat_id))
    dp.register_callback_query_handler(send_menu, not_support_chat_filter, state="*")
    dp.register_message_handler(start, not_support_chat_filter, commands="start", state="*")
    dp.register_message_handler(on_text_question, not_support_chat_filter, state=MenuSG.ask, content_types=ContentTypes.TEXT)
    dp.register_message_handler(on_supported_media_question, not_support_chat_filter, state=MenuSG.ask,  content_types=[
        ContentType.ANIMATION, ContentType.AUDIO, ContentType.PHOTO,
        ContentType.DOCUMENT, ContentType.VIDEO, ContentType.VOICE
    ])
    dp.register_message_handler(on_unsupported_types_question, not_support_chat_filter, state=MenuSG.ask, content_types=ContentTypes.ANY)
    dp.register_message_handler(rerender_on_message, not_support_chat_filter, state="*", content_types=ContentTypes.ANY)
    dp.register_edited_message_handler(edited_message_warning, content_types=ContentTypes.ANY, state=MenuSG.ask)
