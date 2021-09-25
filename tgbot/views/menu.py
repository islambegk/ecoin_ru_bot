import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


texts = {}
for filename in os.listdir("tgbot/views/texts"):
    with open(f"tgbot/views/texts/{filename}", "r") as f:
        texts[filename.split(".")[0]] = f.read()

main = {
    "text": "Главное меню",
    "reply_markup": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Об акции", callback_data="about")],
        [InlineKeyboardButton(text="Наши контакты", callback_data="contacts")],
        [InlineKeyboardButton(text="Полезные материалы", callback_data="materials")],
        [InlineKeyboardButton(text="Задать вопрос", callback_data="ask")]
    ]),
    "disable_web_page_preview": True,
}

about = {
    "text": texts["about"],
    "reply_markup": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Приступить к заданиям",
                              url="http://gorod.plus-one.ru/ecoin/sign-in?utm_source=app&utm_medium=mail&utm_campaign=smm&utm_content=registration&utm_term=ecoin")],
        [InlineKeyboardButton(text="Назад", callback_data="main")]
    ]),
    "disable_web_page_preview": True,
}

contacts = {
    "text": texts["contacts"],
    "reply_markup": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="main")]
    ]),
    "disable_web_page_preview": True,
}

materials = {
    "text": texts["materials"],
    "reply_markup": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="main")]
    ]),
    "disable_web_page_preview": True,
}

ask = {
    "text": texts["ask"],
    "reply_markup": InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="main")]
    ]),
    "disable_web_page_preview": True,
}

menu = {
    "main": main,
    "about": about,
    "contacts": contacts,
    "materials": materials,
    "ask": ask,
}
