from typing import Union

from aioredis.exceptions import WatchError

from aiogram import Dispatcher
from aiogram.types import Message, ContentTypes
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from aiogram.dispatcher.filters import IDFilter

from tgbot.filters.user_question import UserQuestionFilter
from tgbot.filters.reply_to_bot import ReplyToBotFilter
from tgbot.services.repository import Repo
from tgbot.utils.bot import rerender_menu


async def start(message: Message, metrics: dict):
    metrics["action"] = "start_support"
    await message.answer("Бот работает в режиме саппорт-чата.")


async def on_text_answer(message: Message, metrics: dict, repo: Repo):
    metrics["action"] = "answer_text"
    if len(message.text) > 4050:
        return await message.reply("К сожалению, длина этого сообщения превышает допустимый размер в 4050 символов. Попробуйте сократить свой вопрос в новом сообщении или отправить его по частям.")
    
    replied_to_message = message["reply_to_message"]
    question_data = await repo.get_question_data(replied_to_message["message_id"])
    text_to_forward = f"<code>[на связи ecoin]</code>\n\n{message.html_text}"
    try:
        await message.bot.send_message(question_data["chat_id"], text_to_forward, reply_to_message_id=question_data["message_id"], disable_web_page_preview=True)
        await message.reply(f"Сообщение для #{question_data['user_id']} отправлено!")
        question_data["menu_message_id"] = await repo.get_menu_message_id(question_data["user_id"], question_data["chat_id"])
        await rerender_menu(message.bot, question_data)
        try:
            await repo.watch_menu_message_id(question_data["user_id"], question_data["chat_id"])
            await repo.set_menu_message_id(question_data["menu_message_id"], question_data["user_id"], question_data["chat_id"], as_pipeline=True)
        except WatchError:
            new_menu_message_id = await repo.get_menu_message_id(question_data["user_id"], question_data["chat_id"])
            await repo.set_menu_message_id(new_menu_message_id, question_data["user_id"], question_data["chat_id"], as_pipeline=True)
    except BotBlocked:
        await message.reply("Не удалось отправить сообщение пользователю, т.к. он заблокировал бота")
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение пользователю! Ошибка: {ex}")


async def on_supported_media_answer(message: Message, metrics: dict, repo: Repo):
    metrics["action"] = "answer_media"
    if len(message.caption) > 950:
        return await message.reply("Длина подписи медиафайла превышает допустимый размер в 1000 символов. Попробуйте сократить её в следующем сообщении или отправить отдельно от самого файла.")
    replied_to_message = message["reply_to_message"]
    question_data = await repo.get_question_data(replied_to_message["message_id"])
    caption_sent = (message.caption and message.parse_entities(as_html=True)) or ""
    caption_to_forward = f"{caption_sent}\n\n<code>[на связи ecoin]</code>"
    try:
        await message.copy_to(question_data["chat_id"], caption=caption_to_forward)
        await message.reply(f"Сообщение для #{question_data['user_id']} отправлено!")
        question_data["menu_message_id"] = await repo.get_menu_message_id(question_data["user_id"], question_data["chat_id"])
        await rerender_menu(message.bot, question_data)
        try:
            await repo.watch_menu_message_id(question_data["user_id"], question_data["chat_id"])
            await repo.set_menu_message_id(question_data["menu_message_id"], question_data["user_id"], question_data["chat_id"], as_pipeline=True)
        except WatchError:
            new_menu_message_id = await repo.get_menu_message_id(question_data["user_id"], question_data["chat_id"])
            await repo.set_menu_message_id(new_menu_message_id, question_data["user_id"], question_data["chat_id"], as_pipeline=True)
    except BotBlocked:
        await message.reply("Не удалось отправить сообщение пользователю, т.к. бот заблокирован на их стороне")
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение пользователю! Ошибка: {ex}")


async def on_unsupported_types_answer(message: Message, metrics: dict):
    metrics["action"] = "answer_unsupported"
    # Игнорируем служебные сообщения
    if message.content_type in (
            ContentTypes.NEW_CHAT_MEMBERS, ContentTypes.LEFT_CHAT_MEMBER, ContentTypes.VOICE_CHAT_STARTED,
            ContentTypes.VOICE_CHAT_ENDED, ContentTypes.VOICE_CHAT_PARTICIPANTS_INVITED,
            ContentTypes.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentTypes.NEW_CHAT_PHOTO, ContentTypes.DELETE_CHAT_PHOTO,
            ContentTypes.SUCCESSFUL_PAYMENT, ContentTypes.PROXIMITY_ALERT_TRIGGERED,
            ContentTypes.NEW_CHAT_TITLE):
        return

    await message.reply("К сожалению, этот тип сообщения не поддерживается для пересылки. Попробуйте отправить что-нибудь другое.")


async def edited_message_warning(message: Message, metrics: dict):
    metrics["action"] = "answer_edit"
    await message.reply("К сожалению, редактирование сообщения не поддерживается, так как это может вызвать недопонимание у пользователь. Рекомендуем просто отправить новое сообщение")


async def get_user_info(message: Message, metrics: dict):
    replied_to_message = message.reply_to_message
    if message.text:
        user_id = replied_to_message.text.split("\n\n")[0].split("#")[-1]
    else:
        return replied_to_message.caption.split("\n\n")[-1].split("#")[-1]
    metrics["action"] = f"user_info:{user_id}"

    try:
        user = await message.bot.get_chat(user_id)
    except TelegramAPIError as ex:
        return await message.reply(f"Не удалось получить информацию о пользователе! Ошибка: {ex}")
    username = f"@{user.username}" if user.username else "отсутствует"
    return await message.reply(f"Имя: {user.full_name}\nUsername: {username}\nID: {user.id}")


async def on_ban_unban(message: Message, metrics: dict, repo: Repo):
        replied_to_message = message.reply_to_message
        command = message.get_command()[1:]
        if message.text:
            user_id = replied_to_message.text.split("\n\n")[0].split("#")[-1]
        else:
            user_id = replied_to_message.caption.split("\n\n")[-1].split("#")[-1]
        metrics["action"] = f"{command}:{user_id}"
        
        if command == "ban":
            await repo.set_banned(1, user_id)

            await message.reply(
                    f"Пользователь <code>#{user_id}</code> добавлен в список заблокированных. При попытке отправить сообщение пользователь получит уведомление о том, что заблокирован."
                )
        elif command == "unban":
            await repo.set_banned(0, user_id)
            await message.reply(f"Пользователь <code>#{user_id}</code> разблокирован")


def register_support_chat(dp: Dispatcher, support_chat_id: Union[int, str]):
    support_chat_filter = IDFilter(chat_id=support_chat_id)
    dp.register_edited_message_handler(edited_message_warning, content_types=ContentTypes.ANY)
    dp.register_message_handler(start, support_chat_filter, commands="start")
    dp.register_message_handler(get_user_info, support_chat_filter, UserQuestionFilter(True), commands="who")
    dp.register_message_handler(on_ban_unban, support_chat_filter, UserQuestionFilter(True), commands=["ban", "unban"])
    dp.register_message_handler(on_text_answer, support_chat_filter, UserQuestionFilter(True), content_types=ContentTypes.TEXT)
    dp.register_message_handler(on_supported_media_answer, support_chat_filter, UserQuestionFilter(True), content_types=[
        ContentTypes.ANIMATION, ContentTypes.AUDIO, ContentTypes.PHOTO,
        ContentTypes.DOCUMENT, ContentTypes.VIDEO, ContentTypes.VOICE
    ])
    dp.register_message_handler(on_unsupported_types_answer, support_chat_filter, UserQuestionFilter(True), content_types=ContentTypes.ANY)
