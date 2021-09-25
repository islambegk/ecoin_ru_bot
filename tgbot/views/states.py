from aiogram.dispatcher.filters.state import StatesGroup, State


class MenuSG(StatesGroup):
    main = State()
    about = State()
    contacts = State()
    materials = State()
    faq = State()
    ask = State()
